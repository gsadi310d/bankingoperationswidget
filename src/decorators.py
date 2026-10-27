"""Модуль decorators.py: содержит декораторы для проекта BankingOperationsWidget."""

import functools
import logging
from typing import Any, Callable, Optional, TypeVar

# TypeVar, чтобы сохранить тип возвращаемого значения функции при декорировании
F = TypeVar("F", bound=Callable[..., Any])


def log(filename: Optional[str] = None) -> Callable[[F], F]:
    """
    Декоратор для логирования начала, конца и результата работы функции.

    Если filename задан — пишет в файл.
    Если не задан — пишет в консоль (stderr).

    Логирует:
      - Успех: "<имя_функции> ok"
      - Ошибка: "<имя_функции> error: <тип_ошибки>. Inputs: (<args>, {kwargs})"
    """

    def decorator(func: F) -> F:
        # Настраиваем логгер один раз при создании декоратора
        logger = logging.getLogger(func.__name__)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        if logger.hasHandlers():
            logger.handlers.clear()

        # Объявляем handler как общий тип Handler — один раз, до условия
        handler: logging.Handler

        # Хендлер: файл или консоль — создаём один раз
        if filename:
            handler = logging.FileHandler(filename, encoding="utf-8")
        else:
            handler = logging.StreamHandler()

        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
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
            finally:
                # ВАЖНО: если это FileHandler, закрываем его, чтобы освободить файл
                if isinstance(handler, logging.FileHandler):
                    handler.close()

        return wrapper  # type: ignore[return-value]

    return decorator
