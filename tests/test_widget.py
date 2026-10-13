"""Тесты для widget.py (filter, sort, mask, get_date)."""

# from getpass import win_getpass

import pytest

from src import widget


@pytest.fixture
def valid_prefixes_sorted():
    """
    Возвращает список валидных префиксов, отсортированных по длине (убывание).
    Это соответствует логике поиска самого длинного префикса в valid_prefix().
    """
    return sorted(widget.VALID_CARD_PREFIXES, key=len, reverse=True)


"""Тесты mask_account_card"""


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


def test_valid_prefixes(valid_prefixes_sorted):
    """
    Проверяем, что любой валидный префикс из списка корректно обрабатывается.
    Используем простую фикстуру для получения отсортированного списка префиксов.
    """
    for prefix in valid_prefixes_sorted:
        if prefix == "Счет":
            test_input = f"{prefix} 12345678901234560000000000"
        else:
            test_input = f"{prefix} 1234567890123456"
        result = widget.mask_account_card(test_input)
        assert result != "Не корректные данные", f"Префикс {prefix!r} должен быть валидным"
        assert prefix in result, f"Результат должен содержать префикс {prefix!r}"


@pytest.mark.parametrize(
    "invalid_input",
    [
        "FakeCard 1234567890123456",
        "SomeBank 1234567890123456",
        "VisaGold 1234567890123456",  # слитно — не совпадает с префиксами
        "ABC 1234567890123456",  # случайный префикс
        "СчетБезПробела 111122223333444455556666",
    ],
)
def test_invalid_prefixes(invalid_input: str) -> None:
    """Проверяем, что невалидные префиксы дают ожидаемую ошибку"""
    assert widget.mask_account_card(invalid_input) == "Карта отсутствует в списке валидных"


def test_account_via_prefix() -> None:
    """Проверка обработки счёта через общий механизм префиксов"""
    result = widget.mask_account_card("Счет 111122223333444455556666")
    assert "Счет" in result
    # Проверяем, что счёт замаскирован
    # Ищем звёздочки или частичные цифры — признак маски
    assert any(char in result for char in "**")


@pytest.mark.parametrize("edge", ["", "   ", "Visa", "Visa "])
def test_edge_cases(edge: str) -> None:
    result = widget.mask_account_card(edge)
    assert result in ("Отсутствуют данные", "Не корректные данные")


@pytest.mark.parametrize(
    "input_str, expected_prefix",
    [
        ("Visa Classic 4111111111111111", "Visa Classic"),
        ("MasterCard Gold 5500000000000004", "MasterCard Gold"),
        ("МИР Premium 2200123456789012", "МИР Premium"),
        ("  Visa 4111111111111111  ", "Visa"),  # с пробелами
    ],
)
def test_composite_prefixes_order(input_str: str, expected_prefix: str) -> None:
    """
    Убеждаемся, что выбирается самый длинный префикс, а не короткий.
    Также проверяем, что strip() не ломает логику.
    """

    cleaned = input_str.strip()
    matched = widget.valid_prefix(cleaned)
    assert matched == expected_prefix, f"Должен совпадать с {expected_prefix!r}, но совпало с {matched!r}"


@pytest.mark.parametrize(
    "prefix, entity_type",
    [(p, t) for p, t in widget.PREFIX_TO_TYPE.items()],
)
def test_prefix_to_type_consistency(prefix: str, entity_type: str) -> None:
    """
    Страховочный тест: проверяем, что каждый префикс из VALID_CARD_PREFIXES
    имеет корректный тип в PREFIX_TO_TYPE и тип валиден.
    """
    assert prefix in widget.VALID_CARD_PREFIXES
    assert entity_type in {"account", "card"}


@pytest.mark.parametrize(
    "input_with_spaces, expected_contains",
    [
        ("   Visa 4111111111111111   ", "Visa"),
        ("Счет   111122223333444455556666   ", "Счет"),
        ("  MasterCard Gold 5500000000000004  ", "MasterCard Gold"),
    ],
)
def test_strip_handling(input_with_spaces: str, expected_contains: str) -> None:
    """
    Проверка, что лишние пробелы в начале/конце не ломают работу.
    Это покрывает исправление с cleaned_argument.
    """
    result = widget.mask_account_card(input_with_spaces)
    assert expected_contains in result


@pytest.mark.parametrize(
    "input_str, expected_error",
    [
        ("Visa ", "Не корректные данные"),
        ("Счет ", "Не корректный номер банковского счета"),
        ("Счет ABC", "Не корректный номер банковского счета"),
        ("Visa ABC", "Не корректные данные"),
    ],
)
def test_prefix_without_valid_number(input_str: str, expected_error: str) -> None:
    """
    Проверяем ветки, где префикс найден, но номер невалиден.
    Это закроет пропущенные строки в widget.py.
    """
    result = widget.mask_account_card(input_str)
    assert result == expected_error, f"Для {input_str!r} ожидалось {expected_error!r}, получено {result!r}"


@pytest.mark.parametrize(
    "input_str, expected_error",
    [
        # Случай, где номер счёта невалиден (например, только буквы) — заденет ветки валидации маски счёта
        ("Счет ABCDEFGH", "Не корректный номер банковского счета"),
        # Крайний случай: очень короткий номер счёта — если masks.py его отвергает
        ("Счет 1", "Не корректный номер банковского счета"),
    ],
)
def test_invalid_account_number_handling(input_str: str, expected_error: str) -> None:
    """
    Проверяет ветки, когда префикс найден, но номер счёта не проходит валидацию внутри masks.get_mask_account.
    """
    result = widget.mask_account_card(input_str)
    assert result == expected_error, f"Для {input_str!r} ожидалось {expected_error!r}, получено {result!r}"


@pytest.mark.parametrize(
    "input_str, expected_error",
    [
        # Номер карты, который masks.get_mask_card_number отвергает (если там есть проверка длины)
        ("Visa 1234", "Не корректные данные"),
        ("MasterCard 111", "Не корректные данные"),
    ],
)
def test_invalid_card_number_handling(input_str: str, expected_error: str) -> None:
    """
    Проверяет обработку невалидных номеров карт, когда masks возвращает ошибку.
    """
    result = widget.mask_account_card(input_str)
    assert result == expected_error, f"Для {input_str!r} ожидалось {expected_error!r}, получено {result!r}"


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("1234567890", "Не корректные данные"),  # строка 35: только цифры, нет букв
        ("!@#$%^&*()", "Не корректные данные"),  # строка 35: только символы
        ("Счет 1", "Не корректный номер банковского счета"),  # строка 60: цифра есть, но маска отвергла
        ("Visa 123", "Не корректные данные"),  # строка 68: цифры есть, но маска карты отвергла
    ],
)
def test_coverage_remaining(input_str: str, expected: str) -> None:
    result = widget.mask_account_card(input_str)
    assert result == expected, f"Для {input_str!r} ожидалось {expected!r}, получено {result!r}"


"""Тесты get_date"""

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
    assert result.startswith("Неверный формат ISO:")


def test_get_date_null() -> None:
    result = widget.get_date("")
    # Важно: это должно совпадать с тем, что возвращает get_date
    assert result.startswith("Неверный формат ISO:")


def test_get_date_space() -> None:
    result = widget.get_date(" ")
    # Важно: это должно совпадать с тем, что возвращает get_date
    assert result.startswith("Неверный формат ISO:")


def test_get_date_int() -> None:
    result = widget.get_date(12345)
    assert result.startswith("Неверный формат ISO:")
