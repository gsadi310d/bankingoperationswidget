import json
import os
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, mock_open, patch

import pytest
from requests.exceptions import RequestException

from src.utils import (_get_exchange_rate, _is_cache_valid, _load_cache, _save_cache, convert_transaction_to_rub,
                       load_transactions, normalize_transaction)

# --- load_transactions: граничные случаи и валидация ---

def test_load_transactions_file_not_found():
    """Файл не существует → пустой список."""
    result = load_transactions("/non/existent/path/file.json")
    assert result == []


def test_load_transactions_empty_file(tmp_path):
    """Пустой файл → пустой список."""
    file_path = tmp_path / "empty.json"
    file_path.write_text("")
    assert load_transactions(str(file_path)) == []


def test_load_transactions_invalid_json_file(tmp_path):
    """Невалидный JSON → пустой список (JSONDecodeError)."""
    file_path = tmp_path / "invalid.json"
    file_path.write_text("{not valid json}")
    assert load_transactions(str(file_path)) == []


def test_load_transactions_non_list_root_file(tmp_path):
    """Корень JSON — не список → пустой список."""
    file_path = tmp_path / "object.json"
    data = {"transactions": [{"id": 1, "amount": 100}]}
    file_path.write_text(json.dumps(data))
    assert load_transactions(str(file_path)) == []


def test_load_transactions_valid_list_with_bad_items(tmp_path):
    """Валидный JSON со списком, но с «мусором» среди элементов → мусор отброшен."""
    file_path = tmp_path / "valid.json"
    data = [
        {"id": 1, "amount": 100.5, "currency": "RUB", "type": "deposit"},
        {"id": 2, "amount": -50.0, "currency": "USD", "type": "withdrawal"},
        "not a dict",  # лишний элемент
        None,          # лишний элемент
    ]
    file_path.write_text(json.dumps(data))

    result = load_transactions(str(file_path))

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, dict) for item in result)
    assert result[0]["id"] == 1
    assert result[1]["type"] == "withdrawal"


@patch("src.utils.Path.exists", return_value=True)
@patch("src.utils.Path.open")
def test_load_transactions_mock_valid(mock_open, mock_exists):
    """Мок-проверка: файл существует, json.load возвращает список → он возвращается."""
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_file
    mock_open.return_value = mock_file

    mock_data = [{"id": 1, "amount": 100.5, "currency": "RUB", "type": "deposit"}]
    with patch("src.utils.json.load", return_value=mock_data) as mock_load:
        result = load_transactions("any/path/transactions.json")

    assert result == mock_data
    mock_exists.assert_called_once()
    mock_open.assert_called_once()
    mock_load.assert_called_once_with(mock_file)


@patch("src.utils.Path.exists", return_value=True)
@patch("src.utils.Path.open")
def test_load_transactions_mock_json_error(mock_open, mock_exists):
    """Мок-проверка: json.load выбрасывает JSONDecodeError → возвращается пустой список."""
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_file
    mock_open.return_value = mock_file

    with patch(
        "src.utils.json.load",
        side_effect=json.JSONDecodeError("msg", "doc", 0),
    ) as mock_load:
        result = load_transactions("any/path/transactions.json")

    assert result == []
    mock_exists.assert_called_once()
    mock_open.assert_called_once()
    mock_load.assert_called_once_with(mock_file)


# --- normalize_transaction: нормализация транзакций ---

def test_normalize_transaction_missing_operation_amount():
    tx = {"id": 123}  # вообще нет operationAmount
    result = normalize_transaction(tx)
    assert result == {"amount": None, "currency": ""}


def test_normalize_transaction_valid():
    tx = {"operationAmount": {"amount": 123.45, "currency": {"code": "GBP"}}}
    result = normalize_transaction(tx)
    assert result["amount"] == 123.45
    assert result["currency"] == "GBP"


def test_normalize_transaction_invalid_amount():
    tx = {"operationAmount": {"amount": "not_a_number", "currency": {"code": "USD"}}}
    result = normalize_transaction(tx)
    assert result["amount"] is None
    assert result["currency"] == "USD"


def test_normalize_transaction_none_amount():
    tx = {"operationAmount": {"amount": None, "currency": {"code": "EUR"}}}
    result = normalize_transaction(tx)
    assert result["amount"] is None
    assert result["currency"] == "EUR"


def test_normalize_transaction_missing_currency_code():
    tx = {"operationAmount": {"amount": 50.0, "currency": {}}}  # пустой словарь
    result = normalize_transaction(tx)
    assert result["amount"] == 50.0
    assert result["currency"] == ""


# --- convert_transaction_to_rub: конвертация и обработка ошибок ---

@patch("src.utils._get_exchange_rate", return_value=25.05)
def test_convert_eur_to_rub_success(mock_rate):
    transaction = {"amount": 200, "currency": "EUR"}
    result = convert_transaction_to_rub(transaction)
    assert result == pytest.approx(5010.0, rel=1e-2)
    mock_rate.assert_called_once_with("EUR", "RUB")


def test_convert_rub_no_api_call():
    with patch("src.utils.requests.get") as mock_get:
        transaction = {"amount": 123.45, "currency": "RUB"}
        result = convert_transaction_to_rub(transaction)
        assert result == 123.45
        mock_get.assert_not_called()


@patch("src.utils._get_exchange_rate", return_value=None)
def test_convert_transaction_api_error_returns_zero(mock_rate):
    transaction = {"amount": 100, "currency": "USD"}
    assert convert_transaction_to_rub(transaction) == 0.0


def test_convert_transaction_invalid_amount_cases():
    assert convert_transaction_to_rub({"amount": None, "currency": "USD"}) == 0.0
    assert convert_transaction_to_rub({"amount": "сто рублей", "currency": "USD"}) == 0.0
    assert convert_transaction_to_rub({"currency": "USD"}) == 0.0


# --- _get_exchange_rate: кэш и API ---

@patch("src.utils._is_cache_valid", return_value=True)
@patch("src.utils._load_cache", return_value={"USD_RUB": {"rate": 90.5, "ts": "2026-10-31T00:00:00+00:00"}})
@patch("src.utils._save_cache")
@patch("src.utils.requests.get")
def test_get_exchange_rate_caches_once_per_day(mock_get, mock_save, mock_load, mock_is_valid):
    os.environ["EXCHANGE_RATES_API_KEY"] = "test-key-for-tests"

    rate1 = _get_exchange_rate("USD", "RUB")
    rate2 = _get_exchange_rate("USD", "RUB")

    assert rate1 == 90.5
    assert rate2 == 90.5

    mock_get.assert_not_called()
    mock_save.assert_not_called()


@patch("src.utils._is_cache_valid", return_value=False)
@patch("src.utils._load_cache", return_value={"USD_RUB": {"rate": 89.0, "ts": "2000-01-01T00:00:00+00:00"}})
@patch("src.utils._save_cache")
@patch("src.utils.requests.get")
def test_cache_expired_makes_new_request(mock_get, mock_save, mock_load, mock_is_valid):
    mock_resp = mock_get.return_value
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"rates": {"RUB": 91.0}}

    rate = _get_exchange_rate("USD", "RUB")
    assert rate == 91.0

    mock_get.assert_called_once()
    mock_save.assert_called_once()


@patch("src.utils._is_cache_valid", return_value=True)
@patch("src.utils._load_cache", return_value={})
@patch("src.utils._save_cache")
@patch("src.utils.requests.get")
def test_cached_key_missing_uses_api(mock_get, mock_save, mock_load, mock_is_valid):
    mock_resp = mock_get.return_value
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"rates": {"RUB": 88.5}}

    rate = _get_exchange_rate("USD", "RUB")
    assert rate == 88.5

    mock_get.assert_called_once()
    mock_save.assert_called_once()


@patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": ""}, clear=True)
def test_get_api_key_missing():
    from src.utils import _get_exchange_rate  # Замени на реальное имя функции, где лежит этот код

    result = _get_exchange_rate("USD", "RUB")

    assert result is None


@patch("src.utils.requests.get")
def test_get_exchange_rate_currency_not_found(mock_get):
    from src.utils import _get_exchange_rate

    # Эмулируем ответ API, где вообще нет целевой валюты
    mock_resp = mock_get.return_value
    mock_resp.raise_for_status.return_value = None  # HTTP 200 OK
    mock_resp.json.return_value = {
        "rates": {
            "EUR": 105.0,
            "JPY": 60.0
        }
    }

    # Запрашиваем USD, которого нет в rates
    result = _get_exchange_rate("RUB", "USD")

    # Ожидаем None, потому что rate is None
    assert result is None

    mock_get.assert_called_once()

@patch("src.utils.requests.get", side_effect=requests.ConnectionError("DNS lookup failed"))
def test_get_exchange_rate_network_error(mock_get):
    from src.utils import _get_exchange_rate

    result = _get_exchange_rate("RUB", "USD")

    assert result is None
    mock_get.assert_called_once()

@patch("src.utils.requests.get")
def test_get_exchange_rate_rate_limit_429(mock_get):
    from src.utils import _get_exchange_rate

    # Создаем фейковый response с кодом 429
    mock_resp = mock_get.return_value
    mock_resp.raise_for_status.side_effect = requests.HTTPError("429 Too Many Requests", response=mock_resp)
    mock_resp.status_code = 429

    result = _get_exchange_rate("RUB", "USD")

    assert result is None
    mock_get.assert_called_once()

# --- Кэш: загрузка и ошибки ---

@patch("src.utils.Path.exists", return_value=True)
@patch("src.utils.Path.open")
def test_load_cache_invalid_json(mock_open, mock_exists):
    """Невалидный JSON в кэше → пустой словарь."""
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_file
    mock_open.return_value = mock_file

    mock_file.read.return_value = "{not valid json}"

    result = _load_cache()
    assert result == {}


@patch("os.path.exists", return_value=False)
def test_load_cache_file_missing(mock_exists):
    from pathlib import Path

    from src.utils import _load_cache

    result = _load_cache(Path("fake.json"))
    assert result == {}
    # Опционально: проверить, что exists вызвали ровно один раз
    mock_exists.assert_called_once_with(Path("fake.json"))


"""Тесты для _load_cache: все граничные случаи"""

@patch("src.utils.Path.exists", new_callable=PropertyMock)
def test_load_cache_file_not_exists(mock_exists):
    from src.utils import _load_cache
    mock_exists.return_value = False
    result = _load_cache(Path("fake.json"))
    assert result == {}


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data='{"USD_RUB": {"rate": 90.5, "ts": "2026-11-01T12:00:00+00:00"}}')
def test_load_cache_valid_json(mock_open, mock_exists):
    from pathlib import Path

    from src.utils import _load_cache

    result = _load_cache(Path("fake.json"))

    assert isinstance(result, dict)
    assert "USD_RUB" in result
    assert result["USD_RUB"]["rate"] == 90.5
    assert mock_open.called is True


@patch("src.utils.Path.open", new_callable=mock_open, read_data="{not valid json}")
@patch("src.utils.Path.exists", new_callable=PropertyMock)
def test_load_cache_invalid_json(mock_exists, mock_open):
    from src.utils import _load_cache
    mock_exists.return_value = True
    result = _load_cache(Path("fake.json"))
    assert result == {}


@patch("src.utils.Path.open", new_callable=mock_open, read_data="[1, 2, 3]")
@patch("src.utils.Path.exists", new_callable=PropertyMock)
def test_load_cache_non_dict_root(mock_exists, mock_open):
    from src.utils import _load_cache
    mock_exists.return_value = True
    result = _load_cache(Path("fake.json"))
    assert result == {}


@patch("os.path.exists", return_value=True)
@patch("json.load", side_effect=json.JSONDecodeError("msg", "doc", 0))
@patch("builtins.open")  # Нам не важно, что он открывает, главное — json.load упадет
def test_load_cache_force_exception(mock_open, mock_json_load, mock_exists):
    from src.utils import _load_cache

    result = _load_cache(Path("dummy.json"))

    assert result == {}
    # Проверяем, что open вообще вызвали
    mock_open.assert_called_once()
    # Проверяем, что json.load вызвали и он упал
    mock_json_load.assert_called_once()


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open,
       read_data="123")  # <-- Ключевой момент: валидный JSON, но это список, а не dict
def test_load_cache_valid_json_but_not_dict(mock_open, mock_exists):
    from src.utils import _load_cache

    result = _load_cache(Path("list.json"))

    assert result == {}  # Функция должна вернуть пустой dict, а не сам список
    mock_open.assert_called_once()


"""Тесты для _save_cache: атомарность и запись"""

@patch("os.replace")
@patch("json.dump")
@patch("builtins.open", new_callable=mock_open)
def test_save_cache_writes_correct_data(mock_open, mock_dump, mock_replace):
    from pathlib import Path

    from src.utils import _save_cache

    cache = {
        "USD_RUB": {"rate": 89.0, "ts": "2026-11-01T12:00:00+00:00"},
    }
    path = Path("data/rates_cache.json")
    tmp_path = path.with_suffix(".json.tmp")

    _save_cache(cache, path)

    # open вызван с правильным путём и параметрами
    mock_open.assert_called_once_with(tmp_path, "w", encoding="utf-8")

    # json.dump вызван с переданным объектом файла
    mock_dump.assert_called_once()
    file_obj = mock_dump.call_args.args[1]
    assert file_obj is mock_open.return_value

    mock_replace.assert_called_once_with(str(tmp_path), str(path))


@patch("os.replace", side_effect=OSError("No space left on device"))
@patch("builtins.open")
def test_save_cache_os_replace_failure(mock_open, mock_replace):
    from src.utils import _save_cache

    # Вызываем функцию — она должна тихо завершиться (вернуть None), не выбрасывая исключение
    result = _save_cache({"key": "value"}, Path("dummy.json"))

    assert result is None  # Проверяем, что функция вернула None, как и написано в коде
    mock_replace.assert_called_once()  # Убеждаемся, что os.replace действительно пытались вызвать
    mock_open.assert_called()  # И временный файл тоже пытались создать

"""_now_utc"""


@patch("src.utils.datetime", autospec=True)
def test_now_utc_returns_utc_time(mock_datetime):
    from src.utils import _now_utc

    # Подкладываем фейковое "текущее" время, чтобы тест был детерминированным
    fake_now = datetime(2024, 5, 20, 14, 30, 0, tzinfo=timezone.utc)
    mock_datetime.now.return_value = fake_now

    # Вызываем нашу функцию
    result = _now_utc()

    # 1. Проверяем, что внутри вызвали datetime.now с аргументом timezone.utc
    mock_datetime.now.assert_called_once_with(timezone.utc)

    # 2. Проверяем, что сама функция вернула именно это время
    assert result == fake_now

    # 3. (Опционально, но надежно) Проверяем, что у результата есть tzinfo и это UTC
    assert result.tzinfo is not None
    assert result.tzinfo == timezone.utc

"""Тесты для _is_cache_valid: все форматы времени и ошибки парсинга"""
@patch("src.utils._now_utc")
def test_is_cache_valid_fresh_iso_with_z(mock_now):
    from src.utils import _is_cache_valid
    ts = "2026-10-31T10:00:00Z"
    now = datetime(2026, 10, 31, 11, 0, tzinfo=timezone.utc)
    mock_now.return_value = now

    assert _is_cache_valid(ts) is True


@patch("src.utils._now_utc")
def test_is_cache_valid_expired(mock_now):
    from src.utils import _is_cache_valid
    ts = "2026-10-30T10:00:00+00:00"
    now = datetime(2026, 10, 31, 11, 0, tzinfo=timezone.utc)
    mock_now.return_value = now

    assert _is_cache_valid(ts) is False


def test_is_cache_valid_none_timestamp():
    from src.utils import _is_cache_valid
    assert _is_cache_valid(None) is False


def test_is_cache_valid_invalid_iso():
    from src.utils import _is_cache_valid
    assert _is_cache_valid("not-a-date") is False
    assert _is_cache_valid("") is False


"""Тест на ошибку чтения файла (PermissionError / OSError)"""


@patch("os.path.exists", return_value=True)
@patch("builtins.open", side_effect=PermissionError("No permission"))
def test_load_cache_read_permission_error(mock_open, mock_exists):
    from pathlib import Path

    from src.utils import _load_cache

    result = _load_cache(Path("locked.json"))
    assert result == {}
    mock_open.assert_called_once()

"""Тест на невалидный JSON (UnicodeDecodeError)"""


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"\xff\xfe\x00\x01")  # Битые байты
def test_load_cache_unicode_decode_error(mock_open, mock_exists):
    from pathlib import Path

    from src.utils import _load_cache

    result = _load_cache(Path("corrupted.json"))
    assert result == {}

"""Тест на странный формат даты (не ISO) в _is_cache_valid"""
def test_is_cache_valid_invalid_date_format():
    from src.utils import _is_cache_valid

    # Передаем строку, которую dateutil не сможет распарсить
    assert _is_cache_valid("not-a-date-at-all") is False
    # Пустая строка тоже должна вернуть False
    assert _is_cache_valid("") is False

"""Тест на невалидный JSON в кэше"""

@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="not json at all")
def test_load_cache_invalid_json_content(mock_open, mock_exists):
    from pathlib import Path

    from src.utils import _load_cache

    result = _load_cache(Path("bad.json"))
    assert result == {}
    mock_open.assert_called_once()

"""Тест на ошибку доступа к файлу"""
@patch("os.path.exists", return_value=True)
@patch("builtins.open", side_effect=PermissionError("Permission denied"))
def test_load_cache_permission_error(mock_open, mock_exists):
    from pathlib import Path

    from src.utils import _load_cache

    result = _load_cache(Path("locked.json"))
    assert result == {}
    mock_open.assert_called_once()

"""Тест на невалидную дату"""
def test_is_cache_valid_invalid_date_string():
    from src.utils import _is_cache_valid

    assert _is_cache_valid("2026-13-01T12:00:00Z") is False
    assert _is_cache_valid("not-a-date") is False
    assert _is_cache_valid("") is False
    assert _is_cache_valid(None) is False

"""Тест на граничные значения времени кэша"""

@patch("src.utils._now_utc")
def test_is_cache_valid_boundary_cases(mock_now):
    from src.utils import _is_cache_valid

    base_time = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)

    # Ровно 24 часа назад — НЕ валидно (потому что условие <, а не <=)
    cache_time_fresh = (base_time - timedelta(hours=24)).isoformat()
    mock_now.return_value = base_time
    assert _is_cache_valid(cache_time_fresh) is False

    # Чуть меньше 24 часов — валидно
    cache_time_almost_fresh = (base_time - timedelta(hours=23, minutes=59, seconds=59)).isoformat()
    assert _is_cache_valid(cache_time_almost_fresh) is True

    # Чуть больше 24 часов — не валидно
    cache_time_old = (base_time - timedelta(hours=24, minutes=1)).isoformat()
    assert _is_cache_valid(cache_time_old) is False

    # Совсем свежий кэш — валидно
    cache_time_very_fresh = (base_time - timedelta(minutes=5)).isoformat()
    assert _is_cache_valid(cache_time_very_fresh) is True