# tests/test_utils.py
import json
from pathlib import Path

import pytest

from src.utils import get_amount_info, load_transactions


@pytest.fixture
def temp_json_file(tmp_path: Path):
    """
    Фикстура для создания временного JSON-файла в изолированной папке.

    Description:
        Создаёт файл в tmp_path (гарантированно уникальная папка для каждого теста),
        чтобы тесты не зависели от реальных файлов и не ломали структуру проекта.
        Возвращает путь к файлу. После теста файл автоматически удаляется сборщиком pytest.
    """
    file_path = tmp_path / "transactions.json"
    yield str(file_path)


class TestLoadTransactionsBasic:
    def test_empty_file_returns_empty_list(self, temp_json_file: str):
        """
        Проверяет поведение при пустом файле.

        Description:
            Создаётся файл без содержимого.
            Ожидаемое поведение: функция возвращает пустой список [].
            Цель: убедиться, что отсутствие данных обрабатывается корректно, без ошибок.
        """
        Path(temp_json_file).write_text("")
        result = load_transactions(temp_json_file)
        assert result == []

    def test_non_existent_file_returns_empty_list(self):
        """
        Проверяет обработку несуществующего файла.

        Description:
            Передаётся путь к файлу, который точно не существует.
            Ожидаемое поведение: функция сразу возвращает [].
            Цель: гарантировать, что отсутствие файла не вызывает исключение.
        """
        fake_path = "/tmp/this_file_definitely_does_not_exist.json"
        result = load_transactions(fake_path)
        assert result == []

    def test_valid_json_list_of_dicts(self, temp_json_file: str):
        """
        Проверяет загрузку корректного JSON-списка словарей.

        Description:
            В файл записывается валидный JSON: список из двух словарей-транзакций.
            Ожидаемое: функция возвращает список из этих двух словарей без изменений.
            Цель: подтвердить, что валидные данные читаются и возвращаются корректно.
        """
        data = [{"id": 1, "amount": 100.5}, {"id": 2, "amount": 200.0}]
        Path(temp_json_file).write_text(json.dumps(data, ensure_ascii=False))

        result = load_transactions(temp_json_file)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["amount"] == 200.0

    def test_root_is_not_list_returns_empty(self, temp_json_file: str):
        """
        Проверяет случай, когда корень JSON — не список.

        Description:
            В файл записывается JSON-объект (словарь) вместо списка.
            Ожидаемое: функция возвращает [].
            Цель: проверить валидацию структуры на верхнем уровне.
        """
        # ИСПРАВЛЕНО: вместо [...] используем реальный список или пустой список
        data = {"meta": "some info", "transactions": []}  # пустой список вместо [...]
        Path(temp_json_file).write_text(json.dumps(data, ensure_ascii=False))

        result = load_transactions(temp_json_file)
        assert result == []


class TestLoadTransactionsMixedContent:
    def test_mixed_types_in_list_filters_only_dicts(self, temp_json_file: str):
        """
        Проверяет фильтрацию элементов в списке: остаются только словари.

        Description:
            JSON-список содержит разные типы: dict, str, int, None, вложенный список.
            Ожидаемое: функция возвращает только элементы типа dict, остальные игнорируются.
            Цель: убедиться, что функция устойчива к «грязным» данным и не падает.
        """
        data = [
            {"id": 1, "amount": 100},  # dict — должен остаться
            "not a transaction",  # str — игнорируется
            12345,  # int — игнорируется
            None,  # None — игнорируется
            {"id": 2, "amount": 200},  # dict — должен остаться
            [1, 2, 3],  # list — игнорируется
        ]
        Path(temp_json_file).write_text(json.dumps(data, ensure_ascii=False))

        result = load_transactions(temp_json_file)
        assert len(result) == 2
        assert all(isinstance(item, dict) for item in result)
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

    def test_nested_invalid_structure_still_filters_by_top_level(self, temp_json_file: str):
        """
        Проверяет, что фильтрация идёт только по верхнему уровню списка.

        Description:
            Список содержит словари, у которых внутри могут быть любые данные.
            Функция должна оставить все словари верхнего уровня, даже если внутри них «мусор».
            Ожидаемое: все элементы-словари остаются, внутренняя структура не проверяется.
            Цель: показать, что функция не пытается валидировать содержимое словарей.
        """
        data = [
            {"id": 1, "details": "any content, even invalid JSON"},
            {"id": 2, "nested": [1, 2, {"a": "b"}]},
            "string",
            None,
        ]
        Path(temp_json_file).write_text(json.dumps(data, ensure_ascii=False))

        result = load_transactions(temp_json_file)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["nested"][0] == 1  # структура внутри не ломает функцию


class TestLoadTransactionsErrorCases:
    def test_invalid_json_returns_empty(self, temp_json_file: str):
        """
        Проверяет реакцию на невалидный JSON.

        Description:
            В файл пишется текст, который не является валидным JSON (например, «not json»).
            Ожидаемое: функция ловит JSONDecodeError и возвращает [].
            Цель: обеспечить отказоустойчивость при повреждённом файле.
        """
        Path(temp_json_file).write_text("not json at all")
        result = load_transactions(temp_json_file)
        assert result == []

    def test_binary_or_corrupted_encoding_returns_empty(self, temp_json_file: str):
        """
        Проверяет обработку проблем с кодировкой или бинарных данных.

        Description:
            Файл создаётся как бинарный или с некорректной кодировкой.
            Ожидаемое: функция ловит UnicodeDecodeError/OSError и возвращает [].
            Цель: покрыть случаи, когда файл физически есть, но прочитать его нельзя.
        """
        # Записываем байты, которые не являются валидным UTF-8
        with open(temp_json_file, "wb") as f:
            f.write(b"\xff\xfe\x00\x01")

        result = load_transactions(temp_json_file)
        assert result == []

    def test_permissions_error_returns_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """
        Проверяет поведение при ошибке доступа к файлу (permissions).

        Description:
            Через monkeypatch подменяем open так, чтобы он выбрасывал PermissionError.
            Ожидаемое: функция перехватывает ошибку и возвращает [].
            Цель: убедиться, что любые проблемы с доступом к файлу не приводят к падению.
        """
        file_path = str(tmp_path / "locked.json")
        Path(file_path).write_text("{}")

        def raise_permission(*args, **kwargs):
            raise PermissionError("No access")

        monkeypatch.setattr("builtins.open", raise_permission)

        result = load_transactions(file_path)
        assert result == []


""" get_amount_info """


@pytest.mark.parametrize("item, expected", [
    # Формат CSV: плоские поля
    ({"amount": 18687.0, "currency_code": "EUR"}, (18687.0, "EUR")),
    ({"amount": 100, "currency_code": None}, (100, "")),          # без валюты
    # Формат JSON: вложенная структура
    (
        {"operationAmount": {"amount": "67314.10",
                             "currency": {"name": "руб.", "code": "RUB"}}},
        ("67314.10", "RUB"),
    ),
    # JSON без operationAmount
    ({}, (None, "")),
    # operationAmount есть, currency пустая
    ({"operationAmount": {"amount": "100"}}, ("100", "")),
    # Приоритет CSV-полей, если есть и то, и другое
    ({"amount": 5, "currency_code": "USD",
      "operationAmount": {"amount": "999", "currency": {"code": "RUB"}}},
     (5, "USD")),
])
def test_get_amount_info(item, expected):
    assert get_amount_info(item) == expected
