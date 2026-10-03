"""#widget.py Этот модуль будет содержать функции для работы с информацией по картам, считам и датам"""

from datetime import datetime

from . import common, masks


def mask_account_card(in_argument: str) -> str:
    """Фунция шифрования номера катр и счетов"""
    if in_argument.isalpha() or in_argument.isdigit() or common.find_space_position(in_argument) == -1:
        return "Не корректные данные"

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
        if common.find_first_digit_position(number_card) == -1:
            return number_card
        else:
            return in_argument[: char_space + 1] + number_card


def get_date(in_datetime: object) -> str:
    """
    Преобразует строку с датой в формате ISO (с микросекундами) в формат ДД.ММ.ГГГГ.

    Примеры:
        "2024-03-11T02:26:18.671407" -> "11.03.2024"
        некорректная строка -> "Неверный формат ISO: <входная строка>"

    :param in_datetime: строка с датой в формате YYYY-MM-DDTHH:MM:SS.ffffff
    :return: строка в формате ДД.ММ.ГГГГ или сообщение об некоректных данных или формата, если дата невалидна
    """
    if not isinstance(in_datetime, str):
        return f"Неверный тип данных: {in_datetime}"
    try:
        out_datatime = datetime.fromisoformat(in_datetime)
        return out_datatime.strftime("%d.%m.%Y")
    except ValueError:
        return f"Неверный формат ISO: {in_datetime}"
