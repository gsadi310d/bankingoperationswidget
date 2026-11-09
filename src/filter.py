import re
from collections import Counter


def process_bank_search(data:list[dict], search:str)->list[dict]:
    """Возвращает операции, в описании которых есть строка поиска.

    Поиск регистронезависимый, использует регулярные выражения.

    :param data: список словарей с данными о банковских операциях
    :param search: строка поиска
    :return: список словарей с подходящими операциями
    """
    pattern = re.escape(search)  # экранируем спецсимволы регулярок в запросе
    return [
        item for item in data
        if re.search(pattern, str(item.get("description", "")), re.IGNORECASE)
    ]


def process_bank_operations(data: list[dict], categories: list[str]) -> dict:
    """Считает количество операций в каждой из заданных категорий.

    Категория операции определяется по полю description.

    :param data: список словарей с данными о банковских операциях
    :param categories: список названий категорий
    :return: словарь {категория: количество операций}
    """
    matched = [
        item.get("description") for item in data
        if item.get("description") in categories
    ]
    return dict(Counter(matched))
