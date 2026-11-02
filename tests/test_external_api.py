# tests/test_external_api.py
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import RequestException, Timeout

from src.external_api import CACHE_FILE, convert_transaction


@pytest.fixture(autouse=True)
def clean_cache():
    """
    Фикстура для очистки кэша перед каждым тестом.
    Гарантирует, что тесты не зависят от состояния файла rates_cache.json.
    """
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
    yield
    # Опционально: можно удалить кэш и после теста, если он создался
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()


def make_tx(amount: Any, currency_code: str, currency_obj: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Вспомогательная функция для быстрого создания корректной структуры транзакции.

    Description:
        Генерирует JSON-подобную структуру, которую ожидает convert_transaction:
          {
            "operationAmount": {
              "amount": <amount>,
              "currency": {"code": <currency_code>}
            }
          }
        Позволяет легко тестировать граничные случаи, подменяя currency_obj при необходимости.
    """
    if currency_obj is None:
        currency_obj = {"code": currency_code}
    return {
        "operationAmount": {
            "amount": amount,
            "currency": currency_obj,
        }
    }


class TestConvertTransactionBasic:
    def test_rub_no_conversion(self):
        """
        Проверяет, что для валюты RUB конвертация не выполняется.

        Description:
            Тест подаёт транзакцию с валютой RUB и суммой 100.5.
            Ожидаемое поведение: функция возвращает ту же сумму без умножения на курс.
            Цель: убедиться, что логика «если RUB — вернуть сумму» работает корректно.
        """
        tx = make_tx(100.5, "RUB")
        assert convert_transaction(tx) == 100.5

    def test_supported_currency_with_mock_rate(self, clean_cache):
        """
        Проверяет конвертацию для поддерживаемой валюты при наличии валидного кэша.

        Description:
            Мы вручную пишем в кэш курс 90.0 для USD_RUB, который актуален (возраст < 24 часов).
            Подаём транзакцию 100 USD.
            Ожидаемый результат: 9000.0 (100 * 90).
            Цель: проверить, что функция корректно читает кэш и применяет курс, не вызывая API.
        """
        cache_data = {"USD_RUB": {"rate": 90.0, "ts": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()}}
        CACHE_FILE.write_text(json.dumps(cache_data), encoding="utf-8")

        tx = make_tx(100, "USD")
        result = convert_transaction(tx)
        assert result == 9000.0  # 100 * 90

    def test_unsupported_currency(self):
        """
        Проверяет обработку неподдерживаемой валюты.

        Description:
            Подаётся транзакция с валютой XYZ, которой нет в SUPPORTED_CURRENCIES.
            Ожидаемое поведение: функция сразу возвращает 0.0 без попыток получить курс.
            Цель: убедиться, что неподдерживаемые валюты корректно отсекаются.
        """
        tx = make_tx(100, "XYZ")
        assert convert_transaction(tx) == 0.0

    def test_missing_operationAmount(self):
        """
        Проверяет поведение при отсутствии поля operationAmount.

        Description:
            Структура транзакции намеренно «сломана»: нет operationAmount, данные лежат на верхнем уровне.
            Ожидаемое поведение: функция возвращает 0.0.
            Цель: проверить валидацию структуры JSON и защиту от падения на KeyError.
        """
        tx = {"amount": 100, "currency": "USD"}
        assert convert_transaction(tx) == 0.0

    def test_invalid_amount_type(self):
        """
        Проверяет обработку невалидного типа суммы.

        Description:
            В поле amount передаётся строка "not_a_number", которую нельзя преобразовать в float.
            Ожидаемое поведение: функция ловит TypeError/ValueError и возвращает 0.0.
            Цель: убедиться, что некорректные типы данных не ломают функцию.
        """
        tx = make_tx("not_a_number", "USD")
        assert convert_transaction(tx) == 0.0

    def test_none_amount(self):
        """
        Проверяет обработку случая, когда amount равен None.

        Description:
            Поле amount явно установлено в None.
            Ожидаемое поведение: функция возвращает 0.0.
            Цель: покрыть граничный случай отсутствия значения суммы.
        """
        tx = make_tx(None, "USD")
        assert convert_transaction(tx) == 0.0

    def test_missing_currency_code(self):
        """
        Проверяет случай, когда currency есть, но в нём отсутствует поле code.

        Description:
            currency — это словарь, но без ключа code.
            Ожидаемое поведение: функция возвращает 0.0.
            Цель: убедиться, что отсутствие кода валюты обрабатывается корректно.
        """
        tx = {"operationAmount": {"amount": 100, "currency": {}}}  # нет code
        assert convert_transaction(tx) == 0.0

    def test_currency_not_dict(self):
        """
        Проверяет случай, когда поле currency не является словарем.

        Description:
            Вместо словаря currency передаётся строка "USD".
            Ожидаемое поведение: функция проверяет тип и возвращает 0.0.
            Цель: защитить функцию от неожиданных структур JSON.
        """
        tx = {"operationAmount": {"amount": 100, "currency": "USD"}}  # строка вместо dict
        assert convert_transaction(tx) == 0.0


class TestCacheBehavior:
    @patch("src.external_api.datetime")
    def test_cache_fresh_used(self, mock_datetime, clean_cache):
        """
        Проверяет использование свежего кэша и отсутствие запроса к API.

        Description:
            Фиксируем время (mock_datetime), создаём кэш с курсом 85.0, возраст кэша — 5 часов (свежий).
            Подаём транзакцию на 20 USD.
            Ожидаемое: курс берётся из кэша, requests.get не вызывается, результат 1700.0.
            Цель: подтвердить, что свежий кэш используется, а API не дёргается лишний раз.
        """
        now = datetime.now(timezone.utc)
        mock_datetime.now.return_value = now

        cache_data = {"USD_RUB": {"rate": 85.0, "ts": (now - timedelta(hours=5)).isoformat()}}  # свежий
        CACHE_FILE.write_text(json.dumps(cache_data), encoding="utf-8")

        tx = make_tx(20, "USD")
        # Должен взять из кэша, API не должен вызываться
        with patch("src.external_api.requests.get") as mock_get:
            result = convert_transaction(tx)
            mock_get.assert_not_called()

        assert result == 1700.0  # 20 * 85

    @patch("src.external_api.datetime")
    def test_cache_expired_uses_api(self, mock_datetime, clean_cache):
        """
        Проверяет, что просроченный кэш игнорируется и запрос идёт в API.

        Description:
            Кэш искусственно делаем просроченным (возраст 30 часов).
            Мокаем ответ API: курс 90.0 за доллар.
            Подаём 10 USD.
            Ожидаемое: requests.get вызывается один раз, результат 900.0.
            Цель: убедиться, что TTL работает и система переключается на API при устаревании кэша.
        """
        now = datetime.now(timezone.utc)
        mock_datetime.now.return_value = now

        cache_data = {"USD_RUB": {"rate": 80.0, "ts": (now - timedelta(hours=30)).isoformat()}}  # просрочен
        CACHE_FILE.write_text(json.dumps(cache_data), encoding="utf-8")

        # Мокаем ответ API: 90.0 за доллар
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"rates": {"RUB": 90.0}}

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test_key"}):
            with patch("src.external_api.requests.get", return_value=mock_resp) as mock_get:
                tx = make_tx(10, "USD")
                result = convert_transaction(tx)
                mock_get.assert_called_once()

        assert result == 900.0  # 10 * 90

    def test_corrupted_cache_ignored(self, clean_cache):
        """
        Проверяет игнорирование битого кэша и переход на API.

        Description:
            В файл кэша пишется невалидный JSON («not json at all»).
            Мокаем успешный ответ API с курсом 88.0.
            Подаём 5 USD.
            Ожидаемое: кэш игнорируется из‑за ошибки парсинга, вызывается API, результат 440.0.
            Цель: гарантировать отказоустойчивость при повреждении файла кэша.
        """
        # Пишем битый JSON
        CACHE_FILE.write_text("not json at all", encoding="utf-8")

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test_key"}):
            with patch("src.external_api.requests.get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.raise_for_status.return_value = None
                mock_resp.json.return_value = {"rates": {"RUB": 88.0}}
                mock_get.return_value = mock_resp

                tx = make_tx(5, "USD")
                result = convert_transaction(tx)
                # Кэш битый, должен пойти в API
                mock_get.assert_called_once()

        assert result == 440.0  # 5 * 88


class TestApiAndEnvBehavior:
    def test_no_api_key_returns_zero(self, clean_cache):
        """
        Проверяет реакцию на отсутствие API-ключа в окружении.

        Description:
            Очищаем переменные окружения (нет EXCHANGE_RATES_API_KEY).
            Подаём валидную транзакцию в USD.
            Ожидаемое: функция не может запросить курс и возвращает 0.0.
            Цель: убедиться, что отсутствие ключа не приводит к ошибке,
            а обрабатывается как «не удалось конвертировать».
        """
        # Убираем ключ из окружения
        with patch.dict(os.environ, {}, clear=True):
            tx = make_tx(100, "USD")
            assert convert_transaction(tx) == 0.0

    def test_api_error_returns_zero(self, clean_cache):
        """
        Проверяет обработку ошибок сети/API.

        Description:
            requests.get намеренно выбрасывает исключение (имитация сбоя сети).
            Ключ API присутствует.
            Ожидаемое: функция ловит ошибку и возвращает 0.0.
            Цель: обеспечить отказоустойчивость при недоступности внешнего API.
        """
        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test_key"}):
            # Важно: выбрасываем именно RequestException, который ловит функция
            with patch("src.external_api.requests.get", side_effect=RequestException("Network error")):
                tx = {"operationAmount": {"amount": 50, "currency": {"code": "USD"}}}
                result = convert_transaction(tx)

        assert result == 0.0

    @patch("src.external_api.requests.get")
    def test_api_no_rub_rate_returns_zero(self, mock_get, clean_cache):
        """
        Проверяет ситуацию, когда API вернул ответ, но курс RUB отсутствует.

        Description:
            API возвращает JSON, где rates — пустой словарь (нет RUB).
            Ожидаемое: функция трактует это как ошибку конвертации и возвращает 0.0.
            Цель: обработать случай «API ответил, но нужной валюты нет».
        """
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"rates": {}}  # нет RUB
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test_key"}):
            tx = make_tx(100, "USD")
            result = convert_transaction(tx)

        assert result == 0.0

    def test_missing_api_key_returns_zero(self):
        """
        Проверяет поведение при отсутствии API ключа.
        """
        # Убираем ключ из окружения
        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": ""}, clear=True):
            tx = {"operationAmount": {"amount": 100, "currency": {"code": "USD"}}}
            result = convert_transaction(tx)

        assert result == 0.0


class TestCacheWriteFailure:
    @patch("src.external_api.os.replace")
    @patch("src.external_api.Path.open")
    def test_cache_write_failure_does_not_break_conversion(self, mock_open, mock_replace):
        mock_replace.side_effect = OSError("Disk full")
        mock_open.return_value.__enter__.return_value = MagicMock()

        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"rates": {"RUB": 90.0}}

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test_key"}):
            with patch("src.external_api.requests.get", return_value=mock_resp):
                tx = {"operationAmount": {"amount": 10, "currency": {"code": "USD"}}}
                result = convert_transaction(tx)

        assert result == 900.0
        mock_replace.assert_called_once()
        mock_open.assert_called_once()


class TestApiResponseStructureEdgeCases:
    def test_api_response_missing_rates_returns_zero(self):
        """
        Проверяет поведение, когда API вернул JSON без ожидаемой структуры.

        Description:
            Мокаем ответ API так, что в нём нет ключа 'rates' или 'RUB'.
            Ожидаемое поведение: функция корректно обрабатывает отсутствие данных
            и возвращает 0.0, не выбрасывая KeyError.
            Цель: покрыть ветку валидации структуры ответа (строка ~131),
            где rate_raw is None и возвращается 0.0.
        """
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        # Специально возвращаем JSON без 'rates'
        mock_resp.json.return_value = {"other": "data"}

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test_key"}):
            with patch("src.external_api.requests.get", return_value=mock_resp):
                tx = {"amount": 100, "currency": "EUR"}
                result = convert_transaction(tx)

        assert result == 0.0


class TestApiNetworkEdgeCases:
    def test_api_timeout_returns_zero(self):
        """
        Проверяет поведение при сетевом таймауте.
        Здесь должен сработать except RequestException.
        """
        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test_key"}):
            # ИСПРАВЛЕНИЕ 2: Timeout теперь определен
            with patch("src.external_api.requests.get", side_effect=Timeout("Connection timed out")):
                tx = {"operationAmount": {"amount": 100, "currency": {"code": "EUR"}}}
                result = convert_transaction(tx)

        assert result == 0.0

    def test_api_rate_not_float_returns_zero(self, clean_cache):
        """ValueError (невалидное число)"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"rates": {"RUB": "not_a_number"}}

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test_key"}):
            with patch("src.external_api.requests.get", return_value=mock_resp):
                tx = make_tx(10, "USD")
                result = convert_transaction(tx)

        assert result == 0.0
