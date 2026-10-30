"""#utils.py Этот модуль будет содержать функции для работы с JSON-файлами"""

import json
from pathlib import Path
from typing import Any, Dict, List


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает список транзакций из JSON-файла.

    Параметры:
        file_path (str): путь к JSON-файлу.

    Возвращает:
        List[Dict]: список словарей с данными о транзакциях.
                    Возвращает пустой список, если:
                    - файл не найден;
                    - файл пустой;
                    - содержимое не является списком.
    """
    path = Path(file_path)

    # Проверка существования файла
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError, UnicodeDecodeError:
        # Файл невалидный JSON или проблема с кодировкой
        return []

    # Проверяем, что загруженные данные — это список
    if not isinstance(data, list):
        return []

    # Проверка, что элементы списка — словари
    result = [item for item in data if isinstance(item, dict)]

    return result
