# src/utils.py
"""
Этот модуль содержит функции для работы с JSON-файлами транзакций
и конвертации валют.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dateutil import parser as date_parser
from requests.exceptions import RequestException

from src.constants import API_URL

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
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
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


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


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
        now = _now_utc()
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
    except json.JSONDecodeError, UnicodeDecodeError, OSError:
        # Невалидный JSON или проблема с кодировкой — тоже пустой список
        return []

    # Если корень не список — пустой список
    if not isinstance(data, list):
        return []

    # Фильтруем только валидные словари
    result = [item for item in data if isinstance(item, dict)]
    return result


def _get_exchange_rate(base_currency: str, target_currency: str) -> Optional[float]:
    """
    Получает курс обмена валют через внешний API с использованием локального кэша.

    Аргументы:
        base_currency (str): базовая валюта (например, 'USD').
        target_currency (str): целевая валюта (например, 'RUB').

    Возвращает:
        float | None: курс (сколько target_currency за 1 base_currency), либо None,
                       если курс недоступен (нет ключа, лимит API, ошибка сети и т.п.).

    Поведение:
        - Проверяет наличие EXCHANGE_RATES_API_KEY в переменных окружения.
        - Сначала проверяет кэш: если запись есть и не старше CACHE_TTL_HOURS —
          возвращает курс из кэша, не обращаясь к API.
        - Если кэш отсутствует или устарел — делает один HTTP‑запрос к API.
        - При успехе сохраняет курс и текущее UTC‑время в кэш.
        - При любой сетевой ошибке, таймауте или HTTP‑ошибке (включая 429 Too Many Requests)
          возвращает None и не перезаписывает кэш (чтобы не потерять валидные данные).
    """
    api_key = os.getenv("EXCHANGE_RATES_API_KEY")
    if not api_key:
        return None

    cache = _load_cache()
    cache_key = f"{base_currency}_{target_currency}"

    cached_entry = cache.get(cache_key)
    if cached_entry is not None:
        rate = cached_entry.get("rate")
        ts_iso = cached_entry.get("ts")
        if _is_cache_valid(ts_iso):
            # Курс свежий — берём из кэша, API не трогаем
            return float(rate) if rate is not None else None

    # Запрос к API
    params = {
        "base": base_currency,
        "symbols": target_currency,
    }
    headers = {
        "apikey": api_key,
    }

    try:
        resp = requests.get(API_URL, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        rates = data.get("rates", {})
        rate = rates.get(target_currency)

        if rate is None:
            return None

        rate_float = float(rate)

        # Обновляем кэш
        cache[cache_key] = {
            "rate": rate_float,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        _save_cache(cache)

        return rate_float
    except RequestException as e:
        if hasattr(e, "response") and e.response is not None:
            if e.response.status_code == 429:
                # Это лимит — не считаем критичной ошибкой, просто используем кэш
                pass  # или можно раскомментировать для отладки:
                # print("[INFO] Rate limit exceeded (429). Using cached rate or returning None.")
        return None


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


def convert_transaction_to_rub(transaction: Dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли по актуальному курсу.

    Аргументы:
        transaction (dict): нормализованная транзакция с полями 'amount' и 'currency'.

    Возвращает:
        float: сумма в рублях. Если конвертация невозможна — 0.0.

    Поведение:
        - Если валюта уже RUB — возвращает сумму без изменений.
        - Получает курс через _get_exchange_rate.
        - Если курс недоступен — возвращает 0.0.
        - Результат округляется до 2 знаков после запятой.
    """
    amount = transaction.get("amount")
    currency = (transaction.get("currency") or "").upper()

    if amount is None or not isinstance(amount, (int, float)):
        return 0.0

    amount_float = float(amount)

    if currency == "RUB":
        return round(amount_float, 2)

    rate = _get_exchange_rate(currency, "RUB")

    if rate is None:
        return 0.0

    return round(amount_float * rate, 2)
