"""Этот модуль будет содержать функции Фильтрации данных"""

def filter_by_state(in_dict_transaction: list, in_state: str = 'EXECUTED') -> list:
    """Функция фильтрации множества словарей по ключу 'state'"""
    return [in_dict_transaction for in_dict_transaction in in_dict_transaction if
            in_dict_transaction.get('state') == in_state]

def sort_by_date(in_dict_transaction: list, in_reverse: bool = True) -> list:
    """Фунция сортировки множества словарей по дате"""
    pass