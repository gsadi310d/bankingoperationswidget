"""#widget.py Этот модуль будет содержать функции для работы с информацией по картам, считам и датам"""

from datetime import datetime
from typing import FrozenSet
from . import common, masks


# Разрешённые префиксы карт (названия платёжных систем)
# Полный список валидных префиксов (включая подвиды)
# Отсортирован по длине — важно для правильного сопоставления
VALID_CARD_PREFIXES: FrozenSet[str] = frozenset({
    # Visa
    "Visa",
    "Visa Classic",
    "Visa Gold",
    "Visa Platinum",
    "Visa Signature",
    "Visa Infinite",
    "Visa Electron",
    "Visa Business",
    "Visa Corporate",
    # MasterCard
    "MasterCard",
    "MasterCard Standard",
    "MasterCard Gold",
    "MasterCard Platinum",
    "MasterCard World",
    "MasterCard Black",
    "MasterCard Business",
    # American Express
    "AmericanExpress",
    "American Express",
    "AmEx",
    # Maestro
    "Maestro",
    "Maestro Standard",
    "Maestro Premier",
    # МИР
    "МИР",
    "MIR",
    "МИР Premium",
    "МИР Classic",
    "МИР Gold",
    "МИР Platinum",
    # Discover
    "Discover",
    "Discover it",
    # JCB
    "JCB",
    "JCB Standard",
    "JCB Gold",
    # Diners Club
    "DinersClub",
    "Diners Club",
    # UnionPay
    "UnionPay",
    "Union Pay",
    # Cirrus
    "Cirrus",
})


def valid_prefix(in_argument: str) -> str :
    """
    Проверяет, начинается ли строка с одного из VALID_CARD_PREFIXES.
    Возвращает найденный префикс или None.
    Сопоставляет по самому длинному совпадению.
    """
    # Сортируем по длине убыванию — чтобы "Visa Classic" проверился раньше "Visa"
    for prefix in sorted(VALID_CARD_PREFIXES, key=len, reverse=True):
        if in_argument.startswith(prefix):
            return prefix
    return "Катра отсутствует в списке валидных"

def mask_account_card(in_argument: str) -> str:
    """Фунция шифрования номера катр и счетов"""

    if not in_argument:
        return "Отсутствуют данные"

    # if in_argument.isalpha() or in_argument.isdigit() or common.find_space_position(in_argument) == -1:
    #     return "Не корректные данные"

    if in_argument[0:4] == "Счет":
        account_card = masks.get_mask_account(in_argument[5:])
        if common.find_first_digit_position(account_card) == -1:
            return account_card
        else:
            return "Счет " + account_card
    else:
        char_space = common.find_space_position(in_argument)
        while in_argument[char_space + 1].isalpha():
            char_space += common.find_space_position(in_argument[char_space + 1 :]) + 1

        number_card = masks.get_mask_card_number(in_argument[char_space + 1 :])
        if number_card == "Не корректный номер карты":
            return "Не корректные данные"

        if common.find_first_digit_position(number_card) == -1:
            return number_card
        else:
            return in_argument[: char_space + 1] + number_card


def get_date(in_datetime: str) -> str:
    """
    Преобразует строку с датой в формате ISO (с микросекундами) в формат ДД.ММ.ГГГГ.

    Примеры:
        "2024-03-11T02:26:18.671407" -> "11.03.2024"
        некорректная строка -> "Неверный формат ISO: <входная строка>"

    :param in_datetime: строка с датой в формате YYYY-MM-DDTHH:MM:SS.ffffff
    :return: строка в формате ДД.ММ.ГГГГ или сообщение об некоректных данных или формата, если дата невалидна
    """
    # if not isinstance(in_datetime, str):
    #     return f"Неверный тип данных: {in_datetime}"
    try:
        out_datatime = datetime.fromisoformat(str(in_datetime))
        return out_datatime.strftime("%d.%m.%Y")
    # except TypeError:
    #     return f"Неверный тип: {in_datetime}"
    except ValueError:
        return f"Неверный формат ISO: {in_datetime}"
