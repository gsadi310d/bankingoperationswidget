"""Модуль проверки функций masks.py"""

import pytest

from src import masks

"""Тесты get_mask_card"""


@pytest.mark.parametrize(
    "card_number,expected",
    [
        ("7000792289606361", "7000 79** **** 6361"),
        ("1111222233334444", "1111 22** **** 4444"),
        ("1111222233334", "1111 22** *333 4"),
        ("11112222333344", "1111 22** **33 44"),
        ("111122223333444", "1111 22** ***3 444"),
        ("11112222333344445", "1111 22** **** *444 5"),
        ("111122223333444455", "1111 22** **** **44 55"),
        ("1111222233334444555", "1111 22** **** ***4 555"),
    ],
)
def test_get_mask_card_number(card_number: str, expected: str) -> None:
    result = masks.get_mask_card_number(card_number)
    assert result == expected


@pytest.mark.parametrize(
    "account_input",
    [
        "1111",
        "11112222",
        "111122223333",
        "11112222333344445555",
        "111122223333444455556666",
    ],
)
def test_get_mask_card_short_number(account_input: str) -> None:
    result = masks.get_mask_card_number(account_input)
    assert result == "Не корректный номер карты"


@pytest.mark.parametrize(
    "account_input",
    [
        "7000792289a06361",
        "aaaaaaaaaaaaaaaa",
        "aaaa1111bbbb2222ccc",
        "70007922 9606361",
    ],
)
def test_get_mask_card_correct_number(account_input: str) -> None:
    result = masks.get_mask_card_number(account_input)
    assert result == "Не корректный номер карты"


def test_get_mask_card_number_null() -> None:
    assert masks.get_mask_card_number("") == "Номер карты отсутствует"


def test_get_mask_card_number_none() -> None:
    assert masks.get_mask_card_number(None) == "Номер карты отсутствует"


"""Тесты get_mask_account"""


@pytest.mark.parametrize(
    "account,expected",
    [
        ("73654108430135874305", "**4305"),
        ("99998888777766665555", "**5555"),
        ("11112222333344445555", "**5555"),
        ("111122223333444455556666", "**6666"),
        ("1111222233334444555566667777", "**7777"),
    ],
)
def test_get_mask_account(account: str, expected: str) -> None:
    result = masks.get_mask_account(account)
    assert result == expected


@pytest.mark.parametrize(
    "account_input",
    [
        "1111",
        "11112222",
        "111122223333",
        "1111222233334444555",
        "11112222333344445555666677778",
        "11112222333344445555666677778888",
    ],
)
def test_get_mask_short_account(account_input: str) -> None:
    result = masks.get_mask_account(account_input)
    assert result == "Не корректный номер банковского счета"


@pytest.mark.parametrize(
    "account_input",
    [
        "11112222a33344445555",
        "aaaabbbbccccddddeeee",
        "aaaa1111bbbb2222cccc",
        "111122223 3344445555",
    ],
)
def test_get_mask_correct_account(account_input: str) -> None:
    result = masks.get_mask_account(account_input)
    assert result == "Не корректный номер банковского счета"


def test_get_mask_account_null() -> None:
    assert masks.get_mask_account("") == "Номер банковского счета отсутсвует"


def test_get_mask_account_none() -> None:
    assert masks.get_mask_account(None) == "Номер банковского счета отсутсвует"
