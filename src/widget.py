"""#widget.py Этот модуль будет содержать функции для работы с информацией по картам, считам и датам"""

from datetime import datetime
from typing import Any

from src import common, masks

from .constants import PREFIX_TO_TYPE, VALID_CARD_PREFIXES


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


def mask_account_card(in_argument: Any) -> str:
    """Обрабатывает строку с префиксом и номером (карты или счёта) и возвращает
    замаскированный номер либо сообщение об ошибке.

    Логика работы:
      1. Если аргумент пустой, None, NaN или состоит из пробелов — возвращает
         «Отсутствуют данные».
      2. Если в строке нет букв (префикса) — возвращает «Не корректные данные».
      3. Ищет самый длинный валидный префикс из VALID_CARD_PREFIXES.
         Если префикс не найден — возвращает «Карта отсутствует в списке валидных».
      4. Извлекает часть после префикса (номер).
         - Если номер пустой или без цифр — возвращает специфичную ошибку:
             * «Не корректный номер банковского счета» для account,
             * «Не корректные данные» для card.
      5. Для account вызывает masks.get_mask_account; при пустом результате —
         «Не корректный номер банковского счета», иначе «<префикс> <маска>».
      6. Для card вызывает masks.get_mask_card_number; при пустом результате —
         «Не корректные данные», иначе «<префикс> <маска>».

    Примеры:
        >>> mask_account_card("Счет 64686473678894779589")
        'Счет **9589'
        >>> mask_account_card("Visa 4111111111111111")
        'Visa 4111 11** **** 1111'
        >>> mask_account_card("")
        'Отсутствуют данные'
        >>> mask_account_card(float("nan"))
        'Отсутствуют данные'
        >>> mask_account_card("FakeCard 1234")
        'Карта отсутствует в списке валидных'
        >>> mask_account_card("Счет")
        'Не корректный номер банковского счета'

    :param in_argument: входная строка с префиксом и номером
                        (или значение, которое можно привести к строке).
    :return: замаскированный номер в формате «<префикс> <маска>» либо
             сообщение об ошибке.
    """
    if in_argument is None or not str(in_argument).strip():
        return "Отсутствуют данные"

    cleaned_argument = str(in_argument).strip()
    if cleaned_argument.lower() in ("nan", "none"):  # защита от NaN из CSV
        return "Отсутствуют данные"

    # Проверяем, что есть хотя бы буквы (префикс)
    if common.find_first_alpha_position(cleaned_argument) == -1:
        return "Не корректные данные"

    prefix_argument = valid_prefix(cleaned_argument)
    if prefix_argument is None:
        return "Карта отсутствует в списке валидных"

    entity_type = PREFIX_TO_TYPE[prefix_argument]

    # Остаток после префикса и пробела
    number_argument = cleaned_argument[len(prefix_argument) + 1:].strip()

    # Пустой номер или номер без цифр: ошибка зависит от типа
    if not number_argument or common.find_first_digit_position(number_argument) == -1:
        if entity_type == "account":
            return "Не корректный номер банковского счета"
        return "Не корректные данные"

    if entity_type == "account":
        number_account = masks.get_mask_account(number_argument)
        if not number_account:
            return "Не корректный номер банковского счета"
        return f"{prefix_argument} {number_account}"

    # entity_type == "card"
    number_card = masks.get_mask_card_number(number_argument)
    if not number_card:
        return "Не корректные данные"
    return f"{prefix_argument} {number_card}"


def get_date(in_datetime: Any) -> str:
    """Преобразует строку с датой в формате ISO в формат ДД.ММ.ГГГГ.

    Примеры:
        "2024-03-11T02:26:18.671407" -> "11.03.2024"
        некорректная строка -> "Неверный формат ISO: <входная строка>"

    :param in_datetime: строка с датой в формате ISO 8601.
    :return: строка в формате ДД.ММ.ГГГГ или сообщение об ошибке,
             если дата невалидна или формат не ISO.
    """
    if not in_datetime or not isinstance(in_datetime, str):
        return f"Неверный формат ISO: {in_datetime}"

    in_datetime = in_datetime.strip()
    if not in_datetime:
        return "Неверный формат ISO: "

    # Python 3.14+ fromisoformat принимает 24:00:00 (переносит на следующий
    # день по ISO 8601), но по требованиям проекта это ошибка.
    if "T24" in in_datetime:
        return f"Неверный формат ISO: {in_datetime}"

    try:
        out_datetime = datetime.fromisoformat(in_datetime)
        return out_datetime.strftime("%d.%m.%Y")
    except ValueError:
        return f"Неверный формат ISO: {in_datetime}"


def has_value(value: Any) -> bool:
    """True, если значение заполнено и не NaN/None из CSV."""
    """True, если значение заполнено (не пустое и не из пробелов)
    и не является NaN/None из CSV.

    :param value: проверяемое значение.
    :return: True, если значение можно использовать в выводе.
    """
    if value is None:
        return False
    text = str(value).strip()
    return bool(text) and text.lower() not in ("nan", "none")
