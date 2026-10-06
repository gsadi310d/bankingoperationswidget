"""Модуль проверки функций masks.py"""

import pytest

from src import masks


@pytest.mark.parametrize(
    "card_number,expected",
    [
        ("7000792289606361", "7000 79** **** 6361"),
        ("1111222233334444", "1111 22** **** 4444"),
    ],
)
def test_get_mask_card_number(card_number: str, expected: str) -> None:
    result = masks.get_mask_card_number(card_number)
    assert result == expected


@pytest.mark.parametrize(
    "account,expected",
    [
        ("73654108430135874305", "**4305"),
        ("99998888777766665555", "**5555"),
    ],
)
def test_get_mask_account(account: str, expected: str) -> None:
    result = masks.get_mask_account(account)
    assert result == expected


def test_get_mask_card_number_invalid_length() -> None:
    assert masks.get_mask_card_number("12345") == "Не корректный номер карты"


def test_get_mask_account_invalid_length() -> None:
    assert masks.get_mask_account("123") == "Не корректный номер банковского счета"
