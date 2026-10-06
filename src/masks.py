def get_mask_card_number(in_number_card: str) -> str:
    """Функция принимает на вход номер карты и возвращает ее маску"""

    if not in_number_card:
        return "Номер карты отсутствует"

    if not (12 < len(in_number_card) < 20): # длина номера карты может состовлять от 13 до 19 цифр (https://www.alfabank.by/about/wiki/finance/nomer_bankovskoy_karty_i_nomer_scheta/)
        return "Не корректный номер карты"

    if not in_number_card.isdigit():
        return "Не корректный номер карты"

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
        return "Номер банковского счета отсутсвует"

    if  not in_invoice_number.isdigit():
        return "Не корректный номер банковского счета"

    if not (19 < len(in_invoice_number) < 29): # длина банковского счета может состовлять от 20 до 28 цифр (https://www.alfabank.by/about/wiki/finance/nomer_bankovskoy_karty_i_nomer_scheta/)
         return "Не корректный номер банковского счета"

    return "**" + in_invoice_number[-4::]
