# src/utils.py
"""
Этот модуль содержит функции для работы с JSON-файлами транзакций.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from dateutil import parser as date_parser

CACHE_FILE = Path("data/rates_cache.json")
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

CACHE_TTL_HOURS = 24


def _load_cache(path: Path = CACHE_FILE) -> Dict[str, Any]:
    """
    Загружает кэш обменных курсов из JSON-файла.

    Возвращает:
        dict: содержимое кэша как словарь. Если файл не найден или повреждён,
              возвращает пустой словарь {}.

    Поведение:
        - Если файла нет — возвращает {}.
        - Если JSON невалиден или файл нельзя прочитать — возвращает {}.
        - Гарантирует, что результат всегда dict, чтобы избежать ошибок дальше по коду.
    """
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
    except json.JSONDecodeError, UnicodeDecodeError, OSError, FileNotFoundError:
        return {}


def _save_cache(cache: Dict[str, Any], path: Path = CACHE_FILE) -> None:
    """
    Атомарно сохраняет кэш обменных курсов в JSON-файл.

    Аргументы:
        cache (dict): словарь с данными кэша.

    Поведение:
        - Пишет данные во временный файл .tmp.
        - Заменяет основной файл атомарной операцией replace(),
          чтобы при сбое не было частично записанного/битого JSON.
        - Использует indent=2 и ensure_ascii=False для читаемости.
    """
    tmp_path = path.with_suffix(".json.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        # атомарная замена
        os.replace(str(tmp_path), str(path))
    except OSError:
        return None

def _is_cache_valid(ts_str: str | None) -> bool:
    """
    Проверяет, действителен ли кэш на основе ISO‑строки времени.

    Аргументы:
        timestamp_iso (str | None): ISO‑строка времени (например, '2026-10-31T12:00:00+00:00').

    Возвращает:
        bool: True, если с момента timestamp прошло меньше CACHE_TTL_HOURS, иначе False.

    Поведение:
        - Поддерживает суффикс 'Z' (заменяет на '+00:00').
        - Корректно обрабатывает aware/naive datetime, приводя всё к UTC.
        - При ошибке парсинга возвращает False.
    """

    if ts_str is None:
        return False
    try:
        # парсинг ts_str ...
        cache_time = date_parser.isoparse(ts_str)
        now = datetime.now(timezone.utc)
        return (now - cache_time) < timedelta(hours=24)
    except Exception:
        return False


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
    path = Path(file_path)

    # Если файла нет — возвращаем пустой список (не None!)
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError, UnicodeDecodeError, OSError, FileNotFoundError:
        # Невалидный JSON или проблема с кодировкой — тоже пустой список
        return []

    # Если корень не список — пустой список
    if not isinstance(data, list):
        return []

    # Фильтруем только валидные словари
    result = [item for item in data if isinstance(item, dict)]
    return result


def normalize_transaction(tx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Нормализует структуру транзакции к плоскому виду, пригодному для конвертации.

    Аргументы:
        tx (dict): исходная транзакция в сложной вложенной структуре.

    Возвращает:
        dict: нормализованный словарь с ключами 'amount' (float | None) и 'currency' (str).

    Поведение:
        - Ожидает поле 'operationAmount' с вложенными 'amount' и 'currency.code'.
        - Если 'operationAmount' отсутствует — возвращает {'amount': None, 'currency': ''}.
        - Пытается преобразовать amount в float; при ошибке — None.
        - Валюту приводит к верхнему регистру (например, 'usd' → 'USD').
    """
    if "operationAmount" not in tx:
        return {"amount": None, "currency": ""}

    op_amount = tx["operationAmount"]
    amount_raw = op_amount.get("amount")
    currency_info = op_amount.get("currency", {})
    currency = currency_info.get("code", "")

    try:
        amount_val = float(amount_raw)
    except TypeError, ValueError:
        amount_val = None

    return {
        "amount": amount_val,
        "currency": currency.upper(),
    }
