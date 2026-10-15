from typing import Any, Dict, Iterable, Iterator


def filter_by_currency(transactions: Iterable[Dict[str, Any]], currency_code: str) -> Iterator[Dict[str, Any]]:
    """
    Генератор, который фильтрует транзакции по коду валюты.

    Возвращает итератор, выдающий транзакции, где operationAmount.currency.code
    совпадает с переданным currency_code (регистронезависимо).

    :param transactions: Итерируемый объект со словарями транзакций.
    :param currency_code: Код валюты (например, "USD").
    :return: Итератор по отфильтрованным транзакциям.
    """
    target_code = currency_code.upper()

    for transaction in transactions:
        # Безопасный доступ к вложенным ключам с проверкой существования
        amount_data = transaction.get("operationAmount", {})
        currency_data = amount_data.get("currency", {})
        code = currency_data.get("code")

        if code and code.upper() == target_code:
            yield transaction


def transaction_descriptions(transactions: Iterable[Dict[str, Any]]) -> Iterator[str]:
    """
    Генератор, который последовательно возвращает поле description из транзакций.

    Если у транзакции нет поля description или оно пустое, возвращается строка "Без описания".

    :param transactions: Итерируемый объект со словарями транзакций.
    :return: Итератор по строкам описаний операций.
    """
    for transaction in transactions:
        description = transaction.get("description")
        if description and isinstance(description, str) and description.strip():
            yield description.strip()
        else:
            yield "Без описания"


def card_number_generator(start: int, end: int) -> Iterator[str]:
    """
    Генератор номеров банковских карт в формате XXXX XXXX XXXX XXXX.

    Принимает диапазон целых чисел (от 1 до 9999999999999999) и возвращает
    строки с номерами, дополненными нулями до 16 цифр и разбитыми на группы по 4.

    :param start: Начальное число диапазона (включительно).
    :param end: Конечное число диапазона (включительно).
    :return: Итератор по строкам номеров карт.
    """
    if start < 0 or end < 0:
        raise ValueError("Номера карт не могут быть отрицательными.")
    if start > end:
        return  # Пустой итератор, если диапазон некорректен

    for number in range(start, end + 1):
        # Преобразуем число в строку, дополняем нулями слева до 16 символов
        full_number = f"{number:016d}"

        # Разбиваем на группы по 4 цифры через пробел
        formatted_number = f"{full_number[:4]} {full_number[4:8]} {full_number[8:12]} {full_number[12:]}"

        yield formatted_number
