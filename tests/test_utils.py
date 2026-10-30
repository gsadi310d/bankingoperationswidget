import json
from json import JSONDecodeError
from unittest.mock import MagicMock, patch

import pytest

from src.utils import convert_transaction_to_rub, load_transactions, normalize_transaction


def test_load_transactions_file_not_found():
    # Файл не существует → пустой список
    result = load_transactions("/non/existent/path/file.json")
    assert result == []


def test_load_transactions_empty_file(tmp_path):
    # Пустой файл → пустой список (сработает ветка try/except или просто пустой результат)
    file_path = tmp_path / "empty.json"
    file_path.write_text("")
    assert load_transactions(str(file_path)) == []


def test_load_transactions_invalid_json_file(tmp_path):
    # Невалидный JSON → пустой список (попадает в except JSONDecodeError)
    file_path = tmp_path / "invalid.json"
    file_path.write_text("{not valid json}")
    assert load_transactions(str(file_path)) == []


def test_load_transactions_non_list_root_file(tmp_path):
    # Корень JSON — не список (объект) → пустой список
    file_path = tmp_path / "object.json"
    data = {"transactions": [{"id": 1, "amount": 100}]}
    file_path.write_text(json.dumps(data))
    assert load_transactions(str(file_path)) == []


def test_load_transactions_valid_list_of_dicts(tmp_path):
    # Валидный JSON со списком словарей → возвращается список
    file_path = tmp_path / "valid.json"
    data = [
        {"id": 1, "amount": 100.5, "currency": "RUB", "type": "deposit"},
        {"id": 2, "amount": -50.0, "currency": "USD", "type": "withdrawal"},
        "not a dict",  # лишний элемент — должен быть отброшен
        None,  # лишний элемент — должен быть отброшен
    ]
    file_path.write_text(json.dumps(data))

    result = load_transactions(str(file_path))

    assert isinstance(result, list)
    assert len(result) == 2  # только словари
    assert all(isinstance(item, dict) for item in result)
    assert result[0]["id"] == 1
    assert result[1]["type"] == "withdrawal"


"""Тесты с моками (опционально, для проверки вызовов)"""


def test_load_transactions_mock_valid():
    mock_data = [{"id": 1, "amount": 100.5, "currency": "RUB", "type": "deposit"}]

    # Мок для файла (чтобы контекстный менеджер работал)
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_file

    with patch("src.utils.Path.exists", return_value=True) as mock_exists:
        with patch("src.utils.Path.open", return_value=mock_file) as mock_open:
            with patch("src.utils.json.load", return_value=mock_data) as mock_load:
                result = load_transactions("any/path/transactions.json")

    assert result == mock_data
    assert isinstance(result, list)

    mock_exists.assert_called_once()
    # Не проверяем аргументы: Path.open(self, mode, encoding) — self скрыт внутри вызова
    mock_open.assert_called_once()
    mock_load.assert_called_once_with(mock_file)


def test_load_transactions_mock_json_error():
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_file

    with patch("src.utils.Path.exists", return_value=True) as mock_exists:
        with patch("src.utils.Path.open", return_value=mock_file) as mock_open:
            with patch("src.utils.json.load", side_effect=JSONDecodeError("msg", "doc", 0)) as mock_load:
                result = load_transactions("any/path/transactions.json")

    assert result == []

    mock_exists.assert_called_once()
    mock_open.assert_called_once()
    mock_load.assert_called_once_with(mock_file)


"""Тесты конвертации """


@patch("src.utils.os.getenv", return_value="fake-key")
@patch("src.utils.requests.get")
def test_convert_usd_to_rub_success(mock_get, mock_getenv):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"rates": {"RUB": 90.5}}
    mock_get.return_value = mock_resp

    transaction = {"amount": 100, "currency": "USD"}
    result = convert_transaction_to_rub(transaction)
    assert result == pytest.approx(9050.0, rel=1e-2)


@patch("src.utils.os.getenv", return_value="fake-key")
@patch("src.utils.requests.get")
def test_convert_eur_to_rub_success(mock_get, mock_getenv):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"rates": {"RUB": 100.2}}
    mock_get.return_value = mock_resp

    transaction = {"amount": 50, "currency": "EUR"}
    result = convert_transaction_to_rub(transaction)
    assert result == pytest.approx(5010.0, rel=1e-2)


def test_convert_rub_no_api_call():
    with patch("src.utils.requests.get") as mock_get:
        transaction = {"amount": 123.45, "currency": "RUB"}
        result = convert_transaction_to_rub(transaction)
        assert result == 123.45
        mock_get.assert_not_called()


@patch("src.utils.os.getenv", return_value=None)
def test_convert_without_api_key(mock_getenv):
    transaction = {"amount": 100, "currency": "USD"}
    assert convert_transaction_to_rub(transaction) == 0.0


@patch("src.utils.os.getenv", return_value="fake-key")
@patch("src.utils.requests.get")
def test_convert_api_error_returns_zero(mock_get, mock_getenv):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = Exception("Network error")
    mock_get.return_value = mock_resp

    transaction = {"amount": 200, "currency": "USD"}
    assert convert_transaction_to_rub(transaction) == 0.0


@patch("src.utils.os.getenv", return_value="fake-key")
@patch("src.utils.requests.get")
def test_convert_transaction_with_bad_api_response(mock_get, mock_getenv):
    # Эмулируем ситуацию, когда сервер вернул JSON, но без нужной структуры
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"no_rates_here": True}  # нет ключа "rates"
    mock_get.return_value = mock_resp

    transaction = {"amount": 100, "currency": "USD"}
    result = convert_transaction_to_rub(transaction)

    assert result == 0.0


@patch("src.utils.os.getenv", return_value="fake-key")
@patch("src.utils.requests.get")
def test_convert_transaction_with_invalid_json_from_api(mock_get, mock_getenv):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None

    # ВАЖНО: кидаем именно тот тип исключения, который реально выбрасывает resp.json()
    mock_resp.json.side_effect = json.JSONDecodeError("Invalid JSON", doc="", pos=0)

    mock_get.return_value = mock_resp

    transaction = {"amount": 100, "currency": "USD"}
    result = convert_transaction_to_rub(transaction)

    assert result == 0.0
    # Эта проверка гарантирует, что код реально дошел до запроса, а не вернулся раньше
    mock_get.assert_called_once()


@patch("src.utils.os.getenv", return_value="fake-key")
@patch("src.utils.requests.get")
def test_convert_transaction_with_api_json_error(mock_get, mock_getenv):
    # Создаем мок-ответ
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None

    # ГЛАВНОЕ: эмулируем ошибку при вызове .json()
    # Используем Exception, чтобы гарантированно попасть в любой блок except Exception
    mock_resp.json.side_effect = Exception("Simulated JSON decode error")

    mock_get.return_value = mock_resp

    # Важно: используем валюту, которая ТРЕБУЕТ запрос к API (не RUB)
    transaction = {"amount": 100, "currency": "USD"}

    result = convert_transaction_to_rub(transaction)

    assert result == 0.0


def test_convert_transaction_to_rub_invalid_amount():
    # Проверяем случай, когда amount = None
    assert convert_transaction_to_rub({"amount": None, "currency": "USD"}) == 0.0

    # Проверяем случай, когда amount — строка (не число)
    assert convert_transaction_to_rub({"amount": "сто рублей", "currency": "USD"}) == 0.0

    # Проверяем случай, когда вообще нет ключа amount
    assert convert_transaction_to_rub({"currency": "USD"}) == 0.0


def test_normalize_transaction_missing_operation_amount():
    """Ветка: в транзакции нет поля operationAmount."""
    tx = {"id": 123}  # вообще нет operationAmount
    result = normalize_transaction(tx)
    assert result == {"amount": None, "currency": ""}


def test_normalize_transaction_invalid_amount():
    """Ветка: amount не конвертируется в float (TypeError/ValueError)."""
    tx = {"operationAmount": {"amount": "not_a_number", "currency": {"code": "USD"}}}
    result = normalize_transaction(tx)
    assert result["amount"] is None
    assert result["currency"] == "USD"


def test_normalize_transaction_none_amount():
    """Ветка: amount равен None."""
    tx = {"operationAmount": {"amount": None, "currency": {"code": "EUR"}}}
    result = normalize_transaction(tx)
    assert result["amount"] is None
    assert result["currency"] == "EUR"


def test_normalize_transaction_valid():
    """Позитивный кейс: всё на месте и валидно."""
    tx = {"operationAmount": {"amount": 123.45, "currency": {"code": "GBP"}}}
    result = normalize_transaction(tx)
    assert result["amount"] == 123.45
    assert result["currency"] == "GBP"


def test_normalize_transaction_missing_currency_code():
    """Ветка: currency есть, но нет code."""
    tx = {"operationAmount": {"amount": 50.0, "currency": {}}}  # пустой словарь
    result = normalize_transaction(tx)
    assert result["amount"] == 50.0
    assert result["currency"] == ""
