# src/utils.py
"""
Этот модуль содержит функции для работы с JSON-файлами транзакций.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from src.module_logging import setup_logger

logger = setup_logger("utils", "logs/utils.log")


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает список транзакций из JSON-файла.

    Аргументы:
        file_path (str): путь к JSON-файлу с транзакциями.

    Возвращает:
        list[dict]: список словарей-транзакций. Если файл отсутствует, невалиден
                    или структура не соответствует ожиданиям, возвращает [].

    Поведение:
        - Если файл не существует — возвращает [].
        - Если JSON невалиден — возвращает [].
        - Если корень JSON не является списком — возвращает [].
        - Из списка оставляет только элементы типа dict; остальные игнорируются.
        - Не выбрасывает исключения при ошибках чтения или валидации.
    """

    logger.info("Запуск функции load_transactions")

    path = Path(file_path)

    if not path.exists():
        logger.error("Отсутствует путь к файлу")
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError, OSError, FileNotFoundError):
        logger.error("Невалидный JSON или проблема с чтением — возвращаем пустой список")
        return []

    # Если корень не список — пустой список
    if not isinstance(data, list):
        logger.error("Данные не являются списком")
        return []

    logger.info("Функция отработала успешно")
    # Оставляем только словари, остальные элементы игнорируем
    return [item for item in data if isinstance(item, dict)]
