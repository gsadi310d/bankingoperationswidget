"""Этот модуль будет содержать функции для работы с информацией по картам, считам и датам"""
from datetime import datetime

import common
import masks


def mask_account_card(in_argument: str) -> str:
    """Фунция шифрования номера катр и счетов"""
    if in_argument.isalpha() or in_argument.isdigit() or common.find_space_position(in_argument) == -1:
        return "Не корректные данные"

    if in_argument[0:4] == "Счет":
        accaunt = masks.get_mask_account(in_argument[5:-1])
        if common.find_first_digit_position(accaunt) == -1:
            return accaunt
        else:
            return "Счет " + accaunt
    else:
        char_space = common.find_space_position(in_argument)
        while in_argument[char_space + 1].isalpha():
            char_space += common.find_space_position(in_argument[char_space + 1 :]) + 1

        number_card = masks.get_mask_card_number(in_argument[char_space + 1 :])
        if common.find_first_digit_position(number_card) == -1:
            return number_card
        else:
            return in_argument[: char_space + 1] + number_card


def get_date(in_datetime: str) -> str | str:
    """Функция преобразования даты из формата ISO в ДД.ММ.ГГГГ"""
    try:
        out_datatime = datetime.fromisoformat(in_datetime)
        return out_datatime.strftime("%d.%m.%Y")
    except ValueError:
        return f"Неверный формат ISO: {in_datetime}"
    except Exception as out_error:
        return f"Некорректные данные ISO: {in_datetime}"
