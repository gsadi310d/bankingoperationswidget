import json
from json import JSONDecodeError
from unittest.mock import MagicMock, patch

from src.utils import load_transactions


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
