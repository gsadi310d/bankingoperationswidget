import logging

import pytest


@pytest.fixture
def usd_transactions():
    return [
        {
            "id": 1,
            "state": "EXECUTED",
            "date": "2023-01-01T10:00:00",
            "operationAmount": {"amount": "100.00", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод организации",
            "from": "Счет 1",
            "to": "Счет 2",
        },
        {
            "id": 2,
            "state": "CANCELED",
            "date": "2023-01-02T11:00:00",
            "operationAmount": {"amount": "200.00", "currency": {"name": "EUR", "code": "EUR"}},
            "description": "Отменённая операция",
            "from": "Счет 3",
            "to": "Счет 4",
        },
        {
            "id": 3,
            "state": "EXECUTED",
            "date": "2023-01-03T12:00:00",
            "operationAmount": {"amount": "300.00", "currency": {"name": "USD", "code": "usd"}},
            "description": "Перевод со счета на счет",
            "from": "Счет 5",
            "to": "Счет 6",
        },
    ]


@pytest.fixture
def transactions_with_missing_fields():
    # Транзакции без description или без operationAmount/currency
    return [
        {"description": "Нормальное описание"},
        {},
        {"description": ""},
        {"description": "   "},
        {"operationAmount": {}},
        {"operationAmount": {"currency": {}}},
    ]


@pytest.fixture
def empty_transactions():
    return []


@pytest.fixture
def logger_with_handler():
    """Создаёт логгер с уже добавленным хендлером, чтобы сработала ветка handlers.clear()"""
    logger = logging.getLogger("test_func")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.NullHandler())  # NullHandler считается хендлером
    yield logger
    # Опционально: можно очистить после теста, но в нашем случае декоратор сам всё почистит
