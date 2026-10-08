"""#widget.py Этот модуль будет содержать функции для работы с информацией по картам, считам и датам"""

from datetime import datetime
from . import common, masks

from .constants import VALID_CARD_PREFIXES, PREFIX_TO_TYPE


def valid_prefix(in_argument: str) -> str | None:
    """
    Проверяет, начинается ли строка с одного из VALID_CARD_PREFIXES.
    Возвращает найденный префикс или Ошибку "Катра отсутствует в списке валидных".
    Сопоставляет по самому длинному совпадению.
    """
    for prefix in sorted(VALID_CARD_PREFIXES, key=len, reverse=True):
        if in_argument.startswith(prefix):
            next_char_pos = len(prefix)
            # Строка закончилась после префикса (нет номера)
            # или следующий символ — пробел
            if next_char_pos >= len(in_argument) or in_argument[next_char_pos] == " ":
                return prefix
    return None


def mask_account_card(in_argument: str) -> str:
    """
    Обрабатывает строку с префиксом и номером (карты или счёта) и возвращает
    замаскированный номер либо сообщение об ошибке.

    Логика работы:
      1. Если строка пустая или содержит только пробелы — возвращает
         «Отсутствуют данные».
      2. Если в строке нет букв (префикса) — возвращает «Не корректные данные».
      3. Ищет самый длинный валидный префикс из VALID_CARD_PREFIXES.
         Если префикс не найден — возвращает «Карта отсутствует в списке валидных».
      4. Извлекает часть после префикса (номер).
         - Если номер пустой — возвращает специфичную ошибку:
             * «Не корректный номер банковского счета» для типа account,
             * «Не корректные данные» для типа card.
         - Если в номере нет цифр — аналогично возвращает специфичную ошибку.
      5. Для типа account вызывает masks.get_mask_account.
         Если функция вернула ошибку — пробрасывает её.
         Иначе возвращает строку вида «<префикс> <замаскированный_номер>».
      6. Для типа card вызывает masks.get_mask_card_number.
         Если функция вернула ошибку — возвращает «Не корректные данные».
         Иначе возвращает строку вида «<префикс> <замаскированный_номер>».

    Примеры:
        >>> mask_account_card("Счет 64686473678894779589")
        'Счет **9589'
        >>> mask_account_card("Visa 4111111111111111")
        'Visa 4111 11** **** 1111'
        >>> mask_account_card("")
        'Отсутствуют данные'
        >>> mask_account_card("FakeCard 1234")
        'Карта отсутствует в списке валидных'
        >>> mask_account_card("Счет")
        'Не корректный номер банковского счета'

    :param in_argument: входная строка с префиксом и номером.
    :return: замаскированный номер в формате «<префикс> <маска>» либо
             сообщение об ошибке.
    """
    if not in_argument or not in_argument.strip():
        return "Отсутствуют данные"

    cleaned_argument = in_argument.strip()

    # Проверяем, что есть хотя бы буквы (префикс)
    if common.find_first_alpha_position(cleaned_argument) == -1:
        return "Не корректные данные"

    prefix_argument = valid_prefix(cleaned_argument)
    if prefix_argument is None:
        return "Карта отсутствует в списке валидных"

    entity_type = PREFIX_TO_TYPE[prefix_argument]

    # Остаток после префикса и пробела
    number_argument = cleaned_argument[len(prefix_argument) + 1 :].strip()
    # Пустой номер: ошибка зависит от типа
    if not number_argument:
        if entity_type == "account":
            return "Не корректный номер банковского счета"
        return "Не корректные данные"

    # Номер есть, но без цифр
    if common.find_first_digit_position(number_argument) == -1:
        if entity_type == "account":
            return "Не корректный номер банковского счета"
        return "Не корректные данные"

    if entity_type == "account":
        number_account = masks.get_mask_account(number_argument)
        if number_account == "Не корректный номер банковского счета":
            return "Не корректный номер банковского счета"
        return f"{prefix_argument} {number_account}"

    # entity_type == "card"
    number_card = masks.get_mask_card_number(number_argument)
    if number_card == "Не корректный номер карты":
        return "Не корректные данные"
    return f"{prefix_argument} {number_card}"


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
