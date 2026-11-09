import re
from collections import Counter
from typing import Any, Dict, List


def process_bank_search(data: List[Dict[str, Any]], search: str) -> List[Dict[str, Any]]:
    """Возвращает операции, в описании которых есть строка поиска.

    Поиск регистронезависимый, использует регулярные выражения.

    :param data: список словарей с данными о банковских операциях
    :param search: строка поиска
    :return: список словарей с подходящими операциями
    """
    pattern = re.compile(re.escape(search), re.IGNORECASE)
    return [
        item for item in data
        if pattern.search(str(item.get("description", "")))
    ]


def process_bank_operations(data: List[Dict[str, Any]], categories: List[str]) -> Dict[Any, int]:
    """Считает количество операций в каждой из заданных категорий.

    Категория операции определяется по полю description.

    :param data: список словарей с данными о банковских операциях
    :param categories: список названий категорий
    :return: словарь {категория: количество операций}
    """
    categories_set = set(categories)
    matched = [
        item.get("description") for item in data
        if item.get("description") in categories_set
    ]
    return dict(Counter(matched))
