"""#masks.py Модуль преобразования номера в маску"""

from src.module_logging import setup_logger

logger = setup_logger("masks", "logs/masks.log")

def get_mask_card_number(in_number_card: str) -> str:
    """Функция принимает на вход номер карты и возвращает ее маску"""
    logger.info("Запуск модуля get_mask_card_number")
    if not in_number_card:
        logger.error("Номер карты отсутствует")
        return ""

    if not (12 < len(in_number_card) < 20):  # длина номера карты может состовлять от 13 до 19 цифр
        # (https://www.alfabank.by/about/wiki/finance/nomer_bankovskoy_karty_i_nomer_scheta/)
        logger.error("Не корректный номер карты")
        return ""

    if not in_number_card.isdigit():
        logger.error("Не корректный номер карты")
        return ""

    mask_number_card = ""

    if len(in_number_card) % 4 == 0:
        list_number_spaces = [(number + 1) * 4 for number in range(len(in_number_card) // 4 - 1)]
    else:
        list_number_spaces = [(number + 1) * 4 for number in range(len(in_number_card) // 4)]

    for part in range(0, len(in_number_card)):
        if 5 < part < len(in_number_card) - 4:
            for i in in_number_card[part]:
                mask_number_card += "*"
        else:
            mask_number_card += in_number_card[part]
    for part in list_number_spaces[::-1]:
        mask_number_card = mask_number_card[:part] + " " + mask_number_card[part:]

    return mask_number_card


def get_mask_account(in_invoice_number: str) -> str:
    """Функция принимает на вход номер счета и возвращает его маску"""

    if not in_invoice_number:
        logger.error("Номер банковского счета отсутствует")
        return ""

    if not in_invoice_number.isdigit():
        logger.error("Не корректный номер банковского счета")
        return ""

    if not (19 < len(in_invoice_number) < 29):  # длина банковского счета может состовлять от 20 до 28 цифр
        # (https://www.alfabank.by/about/wiki/finance/nomer_bankovskoy_karty_i_nomer_scheta/)
        logger.error("Не корректный номер банковского счета")
        return ""

    return "**" + in_invoice_number[-4::]
