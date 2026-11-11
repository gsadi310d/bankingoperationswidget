from src.filter import process_bank_operations, process_bank_search

""" Тесты process_bank_operations """


def test_process_bank_search_basic():
    """Проверяет базовый поиск по подстроке в описании."""
    data = [
        {"description": "Перевод организации"},
        {"description": "Открытие вклада"},
        {"description": "Покупка в магазине"},
    ]
    result = process_bank_search(data, "перевод")
    assert len(result) == 1
    assert result[0]["description"] == "Перевод организации"


def test_process_bank_search_case_insensitive():
    """Проверяет, что поиск регистронезависимый."""
    data = [{"description": "ПЕРЕВОД ОРГАНИЗАЦИИ"}]
    result = process_bank_search(data, "перевод")
    assert len(result) == 1


def test_process_bank_search_special_chars():
    """Проверяет корректную обработку спецсимволов в запросе (через re.escape)."""
    data = [{"description": "Перевод (со счёта)"}]
    # В запросе скобки — без re.escape это сломало бы регулярное выражение
    result = process_bank_search(data, "(со счёта)")
    assert len(result) == 1


def test_process_bank_search_none_and_float_in_description():
    """Проверяет безопасное приведение None и float к строке без ошибок."""
    data = [
        {"description": None},
        {"description": 123.45},  # float из CSV
        {"description": "Обычный перевод"},
    ]
    result = process_bank_search(data, "перевод")
    assert len(result) == 1
    assert result[0]["description"] == "Обычный перевод"


""" Тесты process_bank_operations """


def test_process_bank_operations_count():
    """Проверяет корректный подсчёт количества операций по категориям."""
    data = [
        {"description": "Перевод организации"},
        {"description": "Перевод организации"},
        {"description": "Открытие вклада"},
        {"description": "Покупка"},  # не входит в категории
    ]
    categories = ["Перевод организации", "Открытие вклада"]
    result = process_bank_operations(data, categories)
    assert result == {"Перевод организации": 2, "Открытие вклада": 1}


def test_process_bank_operations_none_category():
    """Проверяет учёт операций с description=None, если None есть в категориях."""
    data = [{"description": None}]
    result = process_bank_operations(data, [None])
    assert result == {None: 1}


def test_process_bank_operations_empty_data():
    """Проверяет поведение при пустом списке данных."""
    assert process_bank_operations([], ["Категория"]) == {}


def test_process_bank_operations_no_matches():
    """Проверяет пустой результат, если ни одна операция не попадает в категории."""
    data = [{"description": "Другая операция"}]
    result = process_bank_operations(data, ["Перевод организации"])
    assert result == {}
