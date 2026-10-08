def find_first_digit_position(argument: str) -> int:
    """Функция поиска позиции первогго числа в строке"""
    for index, char in enumerate(argument):
        if char.isdigit():
            return index
    return -1  # Возвращаем -1, если цифр в строке нет


def find_first_alpha_position(argument: str) -> int:
    """Функция поиска позиции первой буквы в строке"""
    for index, char in enumerate(argument):
        if char.isalpha():
            return index
    return -1  # Возвращаем -1, если букв в строке нет


def find_space_position(argument: str) -> int:
    """Фунция поиска позици первого пробела в строке"""
    for index, char in enumerate(argument):
        if char == " ":
            return index
    return -1  # Возвращаем -1, если цифр в строке нет
