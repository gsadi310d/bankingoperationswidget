"""Модуль decorators.py: содержит декораторы для проекта BankingOperationsWidget."""

import functools
import logging
from typing import Optional, Callable, Any


def log(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для логирования начала, конца и результата работы функции.

    Если filename задан — пишет в файл.
    Если не задан — пишет в консоль (stderr).

    Логирует:
      - Успех: "<имя_функции> ok"
      - Ошибка: "<имя_функции> error: <тип_ошибки>. Inputs: (<args>, {kwargs})"
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Настраиваем логгер
            logger = logging.getLogger(func.__name__)
            logger.setLevel(logging.INFO)
            logger.propagate = False  # Чтобы не дублировать логи в корневом логгере

            # Очищаем старые хендлеры, чтобы не накапливались при повторных вызовах
            if logger.hasHandlers():
                logger.handlers.clear()

            # Хендлер: файл или консоль
            if filename:
                handler = logging.FileHandler(filename, encoding="utf-8")
            else:
                handler = logging.StreamHandler()

            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            try:
                result = func(*args, **kwargs)
                logger.info(f"{func.__name__} ok")
                return result
            except Exception as e:
                # Формируем строку с входными параметрами как в задании
                inputs_repr = f"({args}, {kwargs})"
                error_type = type(e).__name__
                logger.error(f"{func.__name__} error: {error_type}. Inputs: {inputs_repr}")
                raise  # Пробрасываем ошибку дальше, чтобы поведение функции не менялось
        return wrapper
    return decorator
