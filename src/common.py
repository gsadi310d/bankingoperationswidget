def find_first_digit_position(argument: str) -> str:
    for index, char in enumerate(argument):
        if char.isdigit():
            return index
    return -1  # Возвращаем -1, если цифр в строке нет


def find_space_position(argument: str) -> str:
    for index, char in enumerate(argument):
        if char == " ":
            return index
    return -1  # Возвращаем -1, если цифр в строке нет
