"""#processing.py Этот модуль будет содержать функции Фильтрации данных"""

from datetime import datetime
from typing import Any


def filter_by_state(list_transactions: list[dict[str, Any]], state: str = "EXECUTED") -> list[dict[str, Any]]:
    """
    Фильтрует список словарей по значению ключа 'state'.

    :param list_transactions: список словарей с данными
    :param state: значение для ключа 'state' (по умолчанию 'EXECUTED')
    :return: новый список словарей, где state == переданное значение
    """

    return [transaction for transaction in list_transactions if transaction.get("state") == state]


def sort_by_date(list_transactions: list[dict[str, Any]], in_reverse: bool = True) -> list[dict[str, Any]]:
    """
    Сортирует список словарей по полю 'date' (ISO‑формат).

    :param list_transactions: список словарей с данными
    :param in_reverse: порядок сортировки (True — по убыванию, False — по возрастанию).
                    По умолчанию True (сначала самые последние операции).
    :return: новый отсортированный список (исходный не меняется)
    """

    def parse_date(dict_transactions: dict[str, Any]) -> datetime:
        """
        Безопасное получение даты; если ключа нет или формат неверен, вернём минимальную дату,
        чтобы такие записи оказались в конце при сортировке по убыванию.
        """
        date_str = dict_transactions.get("date")
        if not date_str:
            return datetime.min
        try:
            """Формат ISO 8601 с микросекундами"""
            return datetime.fromisoformat(date_str)
        except ValueError:
            return datetime.min

    return sorted(list_transactions, key=parse_date, reverse=in_reverse)
