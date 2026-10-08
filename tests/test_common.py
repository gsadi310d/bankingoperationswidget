"""Тесты для common.py"""

import pytest
from src import common


@pytest.fixture
def common_test_strings():
    """
    Возвращает словарь с эталонными строками для всех типов проверок.
    """
    return {
        "with_digit": "abc123",
        "digit_at_start": "123abc",
        "mixed_special": "!!!5!!!",
        "empty": "",
        "no_digits": "no_digits_here",
        "spaces_before": "   7",
        "space_between": "a b c 9",

        "with_alpha": "123abc",
        "alpha_at_start": "ABC123",
        "spaces_before_alpha": "  Xyz",
        "only_digits": "123456",
        "only_special": "!@#$%^",
        "digit_then_alpha": "9a",

        "normal_space": "Hello World",
        "no_spaces": "NoSpaces",
        "space_at_start": " Start",
        "space_at_end": "End ",
        "multiple_spaces": "Multiple   Spaces",
        "tab_not_space": "Tab\tSpace",
    }


"""Тесты для find_first_digit_position"""

@pytest.mark.parametrize(
    "input_str, expected_index",
    [
        ("abc123", 3),
        ("123abc", 0),
        ("!!!5!!!", 3),
        ("", -1),
        ("no_digits_here", -1),
        ("   7", 3),
        ("a b c 9", 6),
    ],
)
def test_find_first_digit_position(input_str: str, expected_index: int) -> None:
    result = common.find_first_digit_position(input_str)
    assert result == expected_index, (
        f"Для {input_str!r} ожидалось {expected_index}, но получено {result}"
    )


def test_find_first_digit_position_via_fixture(common_test_strings: dict) -> None:
    data = common_test_strings
    assert common.find_first_digit_position(data["with_digit"]) == 3
    assert common.find_first_digit_position(data["empty"]) == -1
    assert common.find_first_digit_position(data["no_digits"]) == -1
    assert common.find_first_digit_position(data["spaces_before"]) == 3


"""Тесты для find_first_alpha_position"""

@pytest.mark.parametrize(
    "input_str, expected_index",
    [
        ("123abc", 3),
        ("ABC123", 0),
        ("  Xyz", 2),
        ("", -1),
        ("123456", -1),
        ("!@#$%^", -1),
        ("9a", 1),
    ],
)
def test_find_first_alpha_position(input_str: str, expected_index: int) -> None:
    result = common.find_first_alpha_position(input_str)
    assert result == expected_index, (
        f"Для {input_str!r} ожидалось {expected_index}, но получено {result}"
    )


def test_find_first_alpha_position_via_fixture(common_test_strings: dict) -> None:
    data = common_test_strings
    assert common.find_first_alpha_position(data["with_alpha"]) == 3
    assert common.find_first_alpha_position(data["only_digits"]) == -1
    assert common.find_first_alpha_position(data["only_special"]) == -1


"""Тесты для find_space_position"""

@pytest.mark.parametrize(
    "input_str, expected_index",
    [
        ("Hello World", 5),
        ("NoSpaces", -1),
        (" Start", 0),
        ("End ", 3),
        ("Multiple   Spaces", 8),
        ("", -1),
        ("Tab\tSpace", -1),  # \t — это не пробел " "
        ("A B C", 1),
    ],
)
def test_find_space_position(input_str: str, expected_index: int) -> None:
    result = common.find_space_position(input_str)
    assert result == expected_index, (
        f"Для {input_str!r} ожидалось {expected_index}, но получено {result}"
    )


def test_find_space_position_via_fixture(common_test_strings: dict) -> None:
    data = common_test_strings
    assert common.find_space_position(data["normal_space"]) == 5
    assert common.find_space_position(data["no_spaces"]) == -1
    assert common.find_space_position(data["space_at_start"]) == 0
    assert common.find_space_position(data["tab_not_space"]) == -1  # важно: табуляция не считается


# --- Интеграционный тест: как функции работают вместе ---

def test_common_utils_combined_for_prefix_split(common_test_strings: dict) -> None:
    """
    Проверяет совместную работу функций на простой строке: префикс + пробел + номер.
    Используем максимально простой префикс, чтобы не зависеть от длины префикса.
    """
    input_str = "Card 1234567890123456"  # простой и предсказуемый формат

    space_idx = common.find_space_position(input_str)
    assert space_idx == 4, f"Ожидался пробел на позиции 4, но найден на {space_idx}"

    prefix = input_str[:space_idx]
    remainder = input_str[space_idx + 1:]

    # В остатке должна быть цифра на позиции 0
    digit_idx = common.find_first_digit_position(remainder)
    assert digit_idx == 0, f"В остатке {remainder!r} первая цифра должна быть на позиции 0"

    assert prefix == "Card"
    assert remainder == "1234567890123456"


# --- Фикстура для граничных случаев (опционально) ---

@pytest.fixture
def edge_cases():
    """Набор граничных/нестандартных случаев для проверки устойчивости."""
    return [
        "",                 # пустая строка
        "   ",              # только пробелы
        "\t\n",             # только спецсимволы переноса/табуляции
        "1",                # одна цифра
        "A",                # одна буква
        " ",                # один пробел
    ]


def test_edge_cases_all_functions(edge_cases: list) -> None:
    """Прогоняет все три функции по граничным случаям"""
    for s in edge_cases:
        common.find_first_digit_position(s)
        common.find_first_alpha_position(s)
        common.find_space_position(s)
