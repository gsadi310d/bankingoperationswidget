import pytest

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions

"""filter_by_currency"""


@pytest.mark.parametrize(
    "currency_code,expected_count,expected_codes",
    [
        ("USD", 2, ["USD", "usd"]),
        ("EUR", 1, ["EUR"]),
        ("RUB", 0, []),
    ],
    ids=["usd_filter", "eur_filter", "rub_filter"],
)
def test_filter_by_currency_parametrized(usd_transactions, currency_code, expected_count, expected_codes):
    result = list(filter_by_currency(usd_transactions, currency_code))
    assert len(result) == expected_count
    codes = [t["operationAmount"]["currency"]["code"] for t in result]
    assert codes == expected_codes


def test_filter_by_currency_empty_list(empty_transactions):
    result = list(filter_by_currency(empty_transactions, "USD"))
    assert result == []


def test_filter_by_currency_no_matches(usd_transactions):
    result = list(filter_by_currency(usd_transactions, "JPY"))
    assert result == []


def test_filter_by_currency_iterator_behavior(usd_transactions):
    gen = filter_by_currency(usd_transactions, "USD")
    first = next(gen)
    second = next(gen)
    with pytest.raises(StopIteration):
        next(gen)  # больше нет USD-транзакций
    # Проверка, что мы взяли именно первые две USD
    assert first["id"] == 1
    assert second["id"] == 3


"""transaction_descriptions"""


def test_transaction_descriptions_basic(usd_transactions):
    descriptions = list(transaction_descriptions(usd_transactions))
    expected = ["Перевод организации", "Отменённая операция", "Перевод со счета на счет"]
    assert descriptions == expected


def test_transaction_descriptions_missing_and_empty(transactions_with_missing_fields):
    descriptions = list(transaction_descriptions(transactions_with_missing_fields))
    # Ожидаем: нормальное, 3×"Без описания", и ещё 2×"Без описания" из-за отсутствия currency
    expected = [
        "Нормальное описание",
        "Без описания",
        "Без описания",
        "Без описания",
        "Без описания",
        "Без описания",
    ]
    assert descriptions == expected


def test_transaction_descriptions_empty_list(empty_transactions):
    assert list(transaction_descriptions(empty_transactions)) == []


def test_transaction_descriptions_iterator_behavior(usd_transactions):
    gen = transaction_descriptions(usd_transactions)
    first = next(gen)
    second = next(gen)
    third = next(gen)
    with pytest.raises(StopIteration):
        next(gen)
    assert first == "Перевод организации"
    assert second == "Отменённая операция"
    assert third == "Перевод со счета на счет"


"""card_number_generator"""


@pytest.mark.parametrize(
    "start,end,expected",
    [
        (
            1,
            3,
            [
                "0000 0000 0000 0001",
                "0000 0000 0000 0002",
                "0000 0000 0000 0003",
            ],
        ),
        (
            9999999999999998,
            9999999999999999,
            [
                "9999 9999 9999 9998",
                "9999 9999 9999 9999",
            ],
        ),
        (1000, 1000, ["0000 0000 0000 1000"]),
    ],
    ids=["small_range", "max_range_edge", "single_value"],
)
def test_card_number_generator_parametrized(start, end, expected):
    result = list(card_number_generator(start, end))
    assert result == expected


def test_card_number_generator_empty_range():
    result = list(card_number_generator(10, 5))
    assert result == []


def test_card_number_generator_negative_raises():
    with pytest.raises(ValueError, match="Номера карт не могут быть отрицательными"):
        list(card_number_generator(-1, 5))

    with pytest.raises(ValueError, match="Номера карт не могут быть отрицательными"):
        list(card_number_generator(1, -5))


def test_card_number_generator_formatting_consistency():
    # Проверяем, что все номера имеют одинаковый формат XXXX XXXX XXXX XXXX
    result = list(card_number_generator(123, 125))
    for num in result:
        parts = num.split()
        assert len(parts) == 4
        assert all(len(p) == 4 for p in parts)
        assert all(p.isdigit() for p in parts)


def test_card_number_generator_iterator_behavior():
    gen = card_number_generator(5, 8)
    assert next(gen) == "0000 0000 0000 0005"
    assert next(gen) == "0000 0000 0000 0006"
    assert next(gen) == "0000 0000 0000 0007"
    assert next(gen) == "0000 0000 0000 0008"
    with pytest.raises(StopIteration):
        next(gen)
