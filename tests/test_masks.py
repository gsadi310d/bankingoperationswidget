"""Модуль проверки функций masks.py."""

import pytest
from src import masks


# Обычные списки для параметризации (НЕ фикстуры)
VALID_CARD_CASES = [
    ("7000792289606361", "7000 79** **** 6361"),
    ("1111222233334444", "1111 22** **** 4444"),
    ("1111222233334", "1111 22** *333 4"),
    ("11112222333344", "1111 22** **33 44"),
    ("111122223333444", "1111 22** ***3 444"),
    ("11112222333344445", "1111 22** **** *444 5"),
    ("111122223333444455", "1111 22** **** **44 55"),
    ("1111222233334444555", "1111 22** **** ***4 555"),
]

VALID_ACCOUNT_CASES = [
    ("73654108430135874305", "**4305"),
    ("99998888777766665555", "**5555"),
    ("111122223333444455556666", "**6666"),
    ("1" * 24 + "4321", "**4321"),
]


@pytest.fixture
def empty_inputs():
    """Пустые значения (пустая строка)."""
    return [""]


@pytest.fixture
def invalid_card_inputs():
    """Невалидные номера карт: длина не 13–19, есть буквы/пробелы."""
    return [
        "1111",                 # 4 цифры — слишком коротко
        "1" * 20,               # 20 цифр — слишком длинно (20 не входит в 13–19)
        "7000792289a06361",     # 16 символов, но есть буква
        "70007922 9606361",     # 16 символов, но есть пробел
        "aaaaaaaa",             # 8 букв — не цифры и слишком коротко
    ]


@pytest.fixture
def invalid_account_inputs():
    """Невалидные номера счетов: длина не 20–28, есть буквы/пробелы."""
    return [
        "1111",                 # 4 цифры — слишком коротко
        "2" * 19,               # 19 цифр — не входит в 20–28
        "3" * 29,               # 29 цифр — не входит в 20–28
        "11112222a33344445555", # 20 символов, но есть буква
        "111122223 3344445555", # 20 символов, но есть пробел
    ]


"""Тесты для get_mask_card_number"""

@pytest.mark.parametrize("card_number,expected", VALID_CARD_CASES)
def test_get_mask_card_number(card_number: str, expected: str) -> None:
    result = masks.get_mask_card_number(card_number)
    assert result == expected


def test_get_mask_card_empty(empty_inputs: list[str]) -> None:
    for inp in empty_inputs:
        assert masks.get_mask_card_number(inp) == "Номер карты отсутствует"


def test_get_mask_card_invalid_format(invalid_card_inputs: list[str]) -> None:
    for inp in invalid_card_inputs:
        result = masks.get_mask_card_number(inp)
        assert result == "Не корректный номер карты", f"Для {inp!r} ожидалась ошибка, получено: {result!r}"


def test_get_mask_card_none() -> None:
    assert masks.get_mask_card_number(None) == "Номер карты отсутствует"


"""Тесты для get_mask_account"""

@pytest.mark.parametrize("account,expected", VALID_ACCOUNT_CASES)
def test_get_mask_account(account: str, expected: str) -> None:
    result = masks.get_mask_account(account)
    assert result == expected


def test_get_mask_account_empty(empty_inputs: list[str]) -> None:
    for inp in empty_inputs:
        assert masks.get_mask_account(inp) == "Номер банковского счета отсутствует"


def test_get_mask_account_invalid_format(invalid_account_inputs: list[str]) -> None:
    for inp in invalid_account_inputs:
        result = masks.get_mask_account(inp)
        assert result == "Не корректный номер банковского счета", f"Для {inp!r} ожидалась ошибка, получено: {result!r}"


def test_get_mask_account_none() -> None:
    assert masks.get_mask_account(None) == "Номер банковского счета отсутствует"
