import os
from unittest.mock import patch

import pytest
import requests

from src.external_api import _get_exchange_rate, convert_transaction_to_rub

""" Тесты convert_transaction_to_rub """


def test_convert_eur_to_rub_success():
    """
    Проверяет успешную конвертацию транзакции из EUR в RUB.

    Сценарий:
      - Функция _get_exchange_rate мокается и возвращает курс 25.05.
      - На вход подаётся транзакция: amount=200, currency='EUR'.

    Ожидаемый результат:
      - Возвращается сумма 5010.0 (200 * 25.05).
      - _get_exchange_rate вызывается ровно один раз с аргументами ('EUR', 'RUB').
    """
    with patch("src.external_api._get_exchange_rate", return_value=25.05) as mock_rate:
        transaction = {"amount": 200, "currency": "EUR"}
        result = convert_transaction_to_rub(transaction)
        assert result == pytest.approx(5010.0, rel=1e-2)
        mock_rate.assert_called_once_with("EUR", "RUB")


def test_convert_rub_no_api_call():
    """
    Проверяет, что при валюте RUB конвертация не требует обращения к API.

    Сценарий:
      - На вход подаётся транзакция в рублях: amount=123.45, currency='RUB'.
      - Мокается requests.get, чтобы отследить, был ли сделан запрос.

    Ожидаемый результат:
      - Возвращается исходная сумма 123.45 без изменений.
      - requests.get не вызывается ни разу.
    """
    with patch("src.external_api.requests.get") as mock_get:
        transaction = {"amount": 123.45, "currency": "RUB"}
        result = convert_transaction_to_rub(transaction)
        assert result == 123.45
        mock_get.assert_not_called()


def test_convert_transaction_api_error_returns_zero():
    """
    Проверяет обработку ошибки получения курса (None от _get_exchange_rate).

    Сценарий:
      - _get_exchange_rate мокается и возвращает None.
      - На вход подаётся транзакция в USD.

    Ожидаемый результат:
      - Функция возвращает 0.0 вместо падения с ошибкой.
    """
    with patch("src.external_api._get_exchange_rate", return_value=None):
        transaction = {"amount": 100, "currency": "USD"}
        assert convert_transaction_to_rub(transaction) == 0.0


def test_convert_transaction_invalid_amount_cases():
    """
    Проверяет поведение функции при некорректных значениях amount.

    Сценарий:
      - Тестируются три случая: amount=None, amount='сто рублей' (строка), отсутствие ключа amount.
      - Валюта во всех случаях — USD.

    Ожидаемый результат:
      - Во всех трёх случаях функция возвращает 0.0.
    """
    assert convert_transaction_to_rub({"amount": None, "currency": "USD"}) == 0.0
    assert convert_transaction_to_rub({"amount": "сто рублей", "currency": "USD"}) == 0.0
    assert convert_transaction_to_rub({"currency": "USD"}) == 0.0


@patch("src.external_api._get_exchange_rate")
def test_convert_unsupported_currency_returns_zero(mock_rate):
    """
    Проверяет возврат 0.0 для неподдерживаемой валюты без обращения к API.
    """
    transaction = {"amount": 1000, "currency": "JPY"}
    result = convert_transaction_to_rub(transaction)

    assert result == 0.0
    mock_rate.assert_not_called()


""" Тесты _get_exchange_rate """


def test_get_exchange_rate_caches_once_per_day():
    """
    Проверяет работу кэширования: повторный запрос в тот же день не делает новый API-запрос.

    Сценарий:
      - _is_cache_valid возвращает True.
      - _load_cache возвращает валидный кэш с курсом 92.3.
      - Вызывается _get_exchange_rate дважды подряд для пары USD→RUB.

    Ожидаемый результат:
      - Оба вызова возвращают 92.3.
      - requests.get не вызывается (данные берутся из кэша).
      - _save_cache не вызывается повторно.
    """
    with (
        patch("src.external_api._is_cache_valid", return_value=True),
        patch(
            "src.external_api._load_cache", return_value={"USD_RUB": {"rate": 92.3, "ts": "2027-10-31T00:00:00+00:00"}}
        ),
        patch("src.external_api._save_cache") as mock_save,
        patch("src.external_api.requests.get") as mock_req_get,
        patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key-for-tests"}),
    ):
        rate1 = _get_exchange_rate("USD", "RUB")
        rate2 = _get_exchange_rate("USD", "RUB")

        assert rate1 == 92.3
        assert rate2 == 92.3
        mock_req_get.assert_not_called()
        mock_save.assert_not_called()


def test_cache_expired_makes_new_request():
    """
    Проверяет, что при просроченном кэше делается новый запрос к API и обновляется кэш.

    Сценарий:
      - _is_cache_valid возвращает False.
      - _load_cache возвращает старый кэш (2000 год).
      - Эмулируется успешный ответ API с курсом 91.0.

    Ожидаемый результат:
      - Возвращается курс 91.0 из API.
      - requests.get вызывается один раз.
      - _save_cache вызывается один раз для сохранения нового курса.
    """
    with (
        patch("src.external_api._is_cache_valid", return_value=False),
        patch(
            "src.external_api._load_cache", return_value={"USD_RUB": {"rate": 89.0, "ts": "2000-01-01T00:00:00+00:00"}}
        ),
        patch("src.external_api._save_cache") as mock_save,
        patch("src.external_api.requests.get") as mock_req_get,
        patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key-for-tests"}),
    ):
        mock_resp = mock_req_get.return_value
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"rates": {"RUB": 91.0}}

        rate = _get_exchange_rate("USD", "RUB")

        assert rate == 91.0
        mock_req_get.assert_called_once()
        mock_save.assert_called_once()


def test_cached_key_missing_uses_api():
    """
    Проверяет, что при отсутствии нужной валютной пары в кэше делается запрос к API.

    Сценарий:
      - _is_cache_valid возвращает True, но _load_cache возвращает пустой кэш {}.
      - Эмулируется ответ API с курсом 88.5.

    Ожидаемый результат:
      - Возвращается курс 88.5 из API.
      - requests.get вызывается один раз.
      - _save_cache вызывается для сохранения новой пары.
    """
    with (
        patch("src.external_api._is_cache_valid", return_value=True),
        patch("src.external_api._load_cache", return_value={}),
        patch("src.external_api._save_cache") as mock_save,
        patch("src.external_api.requests.get") as mock_req_get,
        patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key-for-tests"}),
    ):
        mock_resp = mock_req_get.return_value
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"rates": {"RUB": 88.5}}

        rate = _get_exchange_rate("USD", "RUB")

        assert rate == 88.5
        mock_req_get.assert_called_once()
        mock_save.assert_called_once()


def test_get_api_key_missing():
    """
    Проверяет поведение при отсутствии API-ключа в переменных окружения.

    Сценарий:
      - EXCHANGE_RATES_API_KEY явно очищается через patch.dict.
      - Запрашивается курс USD→RUB.

    Ожидаемый результат:
      - Функция сразу возвращает None без попыток запроса.
    """
    with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": ""}, clear=True):
        result = _get_exchange_rate("USD", "RUB")
        assert result is None


def test_get_exchange_rate_currency_not_found():
    """
    Проверяет обработку ситуации, когда запрашиваемая валюта отсутствует в ответе API.

    Сценарий:
      - API возвращает курсы для EUR и JPY, но не для RUB (в контексте пары).
      - Запрашивается курс RUB→USD.

    Ожидаемый результат:
      - Функция корректно обрабатывает отсутствие курса и возвращает None.
      - requests.get был вызван один раз.
    """
    with (
        patch("src.external_api.requests.get") as mock_req_get,
        patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key-for-tests"}),
    ):
        mock_resp = mock_req_get.return_value
        mock_resp.raise_for_status.return_value = None
        # В ответе нет RUB для нужной пары
        mock_resp.json.return_value = {"rates": {"EUR": 105.0, "JPY": 60.0}}

        result = _get_exchange_rate("RUB", "USD")

        assert result is None
        mock_req_get.assert_called_once()


def test_get_exchange_rate_network_error():
    """
    Проверяет обработку сетевой ошибки (ConnectionError) при запросе к API.

    Сценарий:
      - requests.get настроен на выброс ConnectionError.
      - Запрашивается курс RUB→USD.

    Ожидаемый результат:
      - Функция перехватывает ошибку и возвращает None.
      - requests.get был вызван ровно один раз.
    """
    with (
        patch("src.external_api.requests.get", side_effect=requests.ConnectionError("DNS lookup failed")),
        patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key-for-tests"}),
    ):
        result = _get_exchange_rate("RUB", "USD")
        assert result is None


def test_get_exchange_rate_rate_limit_429():
    """
    Проверяет обработку HTTP-ошибки 429 Too Many Requests.

    Сценарий:
      - Эмулируется ответ с кодом 429 и соответствующий HTTPError.
      - Запрашивается курс RUB→USD.

    Ожидаемый результат:
      - Ошибка 429 корректно обрабатывается, функция возвращает None.
      - requests.get был вызван один раз.
    """
    with (
        patch("src.external_api.requests.get") as mock_req_get,
        patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key-for-tests"}),
    ):
        mock_resp = mock_req_get.return_value
        mock_resp.status_code = 429
        mock_resp.raise_for_status.side_effect = requests.HTTPError("429 Too Many Requests", response=mock_resp)

        result = _get_exchange_rate("RUB", "USD")

        assert result is None
        mock_req_get.assert_called_once()
