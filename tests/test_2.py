"""Тесты для widget.py (filter, sort, mask, get_date)."""

import pytest

from src import widget

# --- Тесты mask_account_card ---


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("Maestro 1596837868705199", "Maestro 1596 83** **** 5199"),
        ("Счет 64686473678894779589", "Счет **9589"),
        ("MasterCard 7158300734726758", "MasterCard 7158 30** **** 6758"),
        ("Счет 35383033474447895560", "Счет **5560"),
        ("Visa Classic 6831982476737658", "Visa Classic 6831 98** **** 7658"),
        ("Visa Platinum 8990922113665229", "Visa Platinum 8990 92** **** 5229"),
        ("Visa Gold 5999414228426353", "Visa Gold 5999 41** **** 6353"),
        ("Счет 73654108430135874305", "Счет **4305"),
    ],
)
def test_mask_account_card(test_input: str, expected: str) -> None:
    result = widget.mask_account_card(test_input)
    assert result == expected


def test_mask_account_card_account() -> None:
    result = widget.mask_account_card("Счет 64686473678894779589")
    assert "**" in result
    assert "9589" in result


# --- Тесты get_date ---

valid_dates = [
    "14:30:15",
    "03:15:00.999",
    "2023-10-25T14:30:15",
    "2023-10-25T14:30:15.123456",
    "2023-10-25T14:30:15+03:00",
    "2023-10-25T14:30:15-05:00",
    "2024-02-29T12:00:00",
    "2023-10-25T23:59:59.999999",
]


@pytest.mark.parametrize("date_str", valid_dates)
def test_get_date_valid(date_str: str) -> None:
    result = widget.get_date(date_str)
    # Для валидных дат мы ожидаем корректный вывод, а не None
    assert isinstance(result, str)


invalid_dates = [
    "2023-13-01T12:00:00",
    "2023-02-30T00:00:00",
    "2023-10-25T24:00:00",
    "2023-10-25T14:30:15.123.456",
    "2023/10/25T14:30:15",
    "2023-10-25T",
    "2023-10-25T14:30:15abc",
]


@pytest.mark.parametrize("date_str", invalid_dates)
def test_get_date_invalid(date_str: str) -> None:
    result = widget.get_date(date_str)
    assert result.startswith("Неверный формат ISO:")


def test_get_date_none() -> None:
    result = widget.get_date(None)
    # Важно: это должно совпадать с тем, что возвращает get_date
    assert result.startswith("Неверный тип данных:")


def test_get_date_int() -> None:
    result = widget.get_date(12345)
    assert result.startswith("Неверный тип данных:")
