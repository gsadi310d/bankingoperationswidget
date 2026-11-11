"""Модуль проверки функций processing.py"""

from typing import Any

import pytest

from src import processing

"""── Фикстура ──────────────────────────────────────────────────────────"""


@pytest.fixture
def data() -> list[dict[str, Any]]:
    return [
        {"id": 414288290, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
    ]


"""── filter_by_state ──────────────────────────────────────────────────"""


class TestFilterByState:

    def test_filter_default_executed(self, data: list[dict[str, Any]]) -> None:
        """Фильтрация по умолчанию возвращает только EXECUTED."""
        result = processing.filter_by_state(data)
        assert len(result) == 2
        assert all(op["state"] == "EXECUTED" for op in result)
        assert result[0]["id"] == 414288290
        assert result[1]["id"] == 939719570

    def test_filter_canceled(self, data: list[dict[str, Any]]) -> None:
        """Фильтрация по CANCELED возвращает только CANCELED."""
        result = processing.filter_by_state(data, "CANCELED")
        assert len(result) == 2
        assert all(op["state"] == "CANCELED" for op in result)
        assert result[0]["id"] == 594226727
        assert result[1]["id"] == 615064591

    def test_filter_empty_result(self, data: list[dict[str, Any]]) -> None:
        """Фильтр по несуществующему статусу возвращает пустой список."""
        result = processing.filter_by_state(data, "PENDING")
        assert result == []

    def test_filter_does_not_mutate_original(self, data: list[dict[str, Any]]) -> None:
        """Оригинальный список не должен меняться."""
        original_len = len(data)
        processing.filter_by_state(data, "CANCELED")
        assert len(data) == original_len


"""── sort_by_date ──────────────────────────────────────────────────────"""


class TestSortByDate:

    def test_sort_descending_default(self, data: list[dict[str, Any]]) -> None:
        """Сортировка по убыванию (по умолчанию): свежие первыми."""
        result = processing.sort_by_date(data)
        dates = [op["date"] for op in result]
        assert dates == [
            "2019-07-03T18:35:29.512364",
            "2018-10-14T08:21:33.419441",
            "2018-09-12T21:27:25.241689",
            "2018-06-30T02:08:58.425572",
        ]

    def test_sort_ascending(self, data: list[dict[str, Any]]) -> None:
        """Сортировка по возрастанию: старые первыми."""
        result = processing.sort_by_date(data, in_reverse=False)
        dates = [op["date"] for op in result]
        assert dates == [
            "2018-06-30T02:08:58.425572",
            "2018-09-12T21:27:25.241689",
            "2018-10-14T08:21:33.419441",
            "2019-07-03T18:35:29.512364",
        ]

    def test_sort_empty_list(self) -> None:
        """Сортировка пустого списка не падает."""
        assert processing.sort_by_date([]) == []

    def test_sort_does_not_mutate_original(self, data: list[dict[str, Any]]) -> None:
        """Оригинальный список не должен меняться после сортировки."""
        original_order = [op["id"] for op in data]
        processing.sort_by_date(data)
        assert [op["id"] for op in data] == original_order

    """── sort_by_date: граничные случаи и ошибки ─────────────────────────"""


class TestSortByDateEdgeCases:
    def test_sort_with_none_and_empty_dates(self) -> None:
        """
        Проверяет ветку if not date_str:
        None и пустая строка должны уйти в самый конец списка.
        """
        data = [
            {"id": 1, "date": None},
            {"id": 2, "date": ""},
            {"id": 3, "date": "2019-07-03T18:35:29.512364"},
            {"id": 4, "date": "2018-06-30T02:08:58.425572"},
        ]

        result = processing.sort_by_date(data, in_reverse=True)
        ids = [op["id"] for op in result]

        # Валидные даты должны быть первыми (по убыванию)
        assert ids[0] == 3
        assert ids[1] == 4

        # Битые даты (None и "") должны быть в конце
        assert set(ids[-2:]) == {1, 2}

    def test_sort_with_invalid_date_format(self) -> None:
        """
        Проверяет блок except ValueError:
        Невалитный формат даты должен уйти в конец списка.
        """
        data = [
            {"id": 1, "date": "not-a-date"},
            {"id": 2, "date": "2019-07-03T18:35:29.512364"},
            {"id": 3, "date": "bad-format-12"},
        ]

        result = processing.sort_by_date(data, in_reverse=True)
        ids = [op["id"] for op in result]

        # Единственная валидная дата должна быть первой
        assert ids[0] == 2

        # Невалитные должны быть в конце (порядок между ними не важен)
        assert set(ids[-2:]) == {1, 3}

    def test_sort_with_missing_date_key(self) -> None:
        """
        Проверяет случай, когда ключа 'date' вообще нет в словаре.
        dict_transactions.get("date") вернёт None → сработает ветка if not date_str.
        """
        data = [
            {"id": 1},  # нет ключа date
            {"id": 2, "date": "2019-07-03T18:35:29.512364"},
        ]

        result = processing.sort_by_date(data, in_reverse=True)
        ids = [op["id"] for op in result]

        assert ids[0] == 2  # валидная дата выше
        assert ids[1] == 1  # запись без даты внизу
