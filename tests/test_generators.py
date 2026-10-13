import pytest
from src.generators import filter_by_currency, transaction_descriptions, card_number_generator


"""filter_by_currency"""
def test_filter_by_currency_basic():
    transactions = [
        {"operationAmount": {"currency": {"code": "USD"}}},
        {"operationAmount": {"currency": {"code": "RUB"}}},
        {"operationAmount": {"currency": {"code": "usd"}}},  # проверка регистра
    ]

    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 2
    assert result[0]["operationAmount"]["currency"]["code"] == "USD"
    assert result[1]["operationAmount"]["currency"]["code"] == "usd"


def test_filter_by_currency_empty_result():
    transactions = [{"operationAmount": {"currency": {"code": "EUR"}}}]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 0


def test_filter_by_currency_missing_keys():
    # Транзакция без валюты вообще
    transactions = [
        {"operationAmount": {"currency": {"code": "USD"}}},
        {"operationAmount": {}},  # Нет currency
        {},  # Нет operationAmount
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1


"""transaction_descriptions"""
def test_transaction_descriptions_basic():
    transactions = [
        {"description": "Перевод организации"},
        {"description": "Перевод со счета на счет"},
    ]
    result = list(transaction_descriptions(transactions))
    assert result == ["Перевод организации", "Перевод со счета на счет"]


def test_transaction_descriptions_missing_and_empty():
    transactions = [
        {},
        {"description": ""},
        {"description": "   "},
        {"description": "Нормальное описание"},
    ]
    result = list(transaction_descriptions(transactions))
    # Ожидается: 3 раза «Без описания» + 1 нормальное
    assert result == [
        "Без описания",
        "Без описания",
        "Без описания",
        "Нормальное описание",
    ]


def test_transaction_descriptions_iterator_behavior():
    transactions = [{"description": f"Op {i}"} for i in range(10)]
    gen = transaction_descriptions(transactions)
    first_five = [next(gen) for _ in range(5)]
    assert first_five == [f"Op {i}" for i in range(5)]


"""card_number_generator"""
def test_card_number_generator_basic():
    result = list(card_number_generator(1, 3))
    assert result == [
        "0000 0000 0000 0001",
        "0000 0000 0000 0002",
        "0000 0000 0000 0003",
    ]


def test_card_number_generator_large_number():
    # Проверка форматирования большого числа (ровно 16 цифр)
    result = list(card_number_generator(1234567812345678, 1234567812345678))
    assert result == ["1234 5678 1234 5678"]


def test_card_number_generator_empty_range():
    # Если start > end, генератор должен быть пустым
    result = list(card_number_generator(10, 5))
    assert result == []


def test_card_number_generator_iterator_behavior():
    gen = card_number_generator(1000, 1005)
    # Берем первые 3 элемента
    first_three = [next(gen) for _ in range(3)]
    assert first_three == [
        "0000 0000 0000 1000",
        "0000 0000 0000 1001",
        "0000 0000 0000 1002",
    ]


def test_card_number_generator_negative_start():
    with pytest.raises(ValueError, match="Номера карт не могут быть отрицательными"):
        list(card_number_generator(-1, 5))

def test_card_number_generator_negative_end():
    with pytest.raises(ValueError, match="Номера карт не могут быть отрицательными"):
        list(card_number_generator(1, -5))