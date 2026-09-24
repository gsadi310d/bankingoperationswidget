# masks.py


def get_mask_card_number(in_number_card: str) -> str:
    """Функция принимает на вход номер карты и возвращает ее маску"""

    mask_number_card = ""
    list_number_spaces = [(number + 1) * 4 for number in range(len(in_number_card) // 4)]

    if len(in_number_card) < 16:
        return "Не корректный номер карты"

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

    if len(in_invoice_number) < 20:
        return "Не корректный номер банковского счета"

    return "**" + in_invoice_number[-4::]
