# src/external_api.py
"""
Этот модуль содержит функции для конвертации валют.

Из-за ограничений API (100 запросов в месяц)
будет делаться один запрос в сутки и курс сохраняться в data/rates_cache.json
"""

import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional
from pathlib import Path

import requests, json
from requests.exceptions import RequestException

from src.constants import API_URL, SUPPORTED_CURRENCIES
from src.utils import _is_cache_valid, _load_cache, _save_cache
from dateutil import parser as date_parser


CACHE_FILE = Path("data/rates_cache.json")
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

CACHE_TTL_HOURS = 24

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

    # Загрузка cash файла с курсом валют
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


def convert_transaction(transaction: Dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли по актуальному курсу.

    Аргументы:
        transaction (dict): нормализованная транзакция с полями 'amount' и 'currency'.

    Возвращает:
        float: сумма в рублях. Если конвертация невозможна — 0.0.

    Поведение:
        - Если валюта уже RUB — возвращает сумму без изменений.
        - Для валют USD и EUR происходит получение курса через _get_exchange_rate,
          который внутри себя может обращаться к внешнему API (Exchange Rates Data API)
          или использовать локальный кэш (используется если актуальность данных не старше 24 часов).
        - Если курс недоступен (None) или валюта не поддерживается — возвращает 0.0.
        - Результат округляется до 2 знаков после запятой.
    """
    amount = transaction.get("amount")
    currency = (transaction.get("currency") or "").upper()

    try:
        amount_float = float(amount)
        # Если уже рубли — возвращаем как есть
        if currency == "RUB":
            return round(amount_float, 2)

        # По заданию: конвертируем только USD и EUR
        if currency not in SUPPORTED_CURRENCIES:
            # Можно добавить логирование: «Валюта не поддерживается: {currency}»
            return 0.0

        api_key = os.getenv("EXCHANGE_RATES_API_KEY")
        if not api_key:
            return None

        # Если файла нет — Запрос к API с записью в cash
        if not CACHE_FILE.exists():
            #
            params = {"base": currency, "symbols": "RUB", }
            try:
                resp = requests.get(API_URL, params=params, headers=api_key, timeout=5)
                resp.raise_for_status()
                data = resp.json()

                rates = data.get("rates", {})
                rate = rates.get("RUB")

                if rate is None:
                    return None

                rate_float = float(rate)

                # Обновляем кэш
                tmp_path = CACHE_FILE.with_suffix(".json.tmp")
                try:
                    with open(tmp_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    # атомарная замена
                    os.replace(str(tmp_path), str(CACHE_FILE))
                except OSError:
                    return None
                CACHE_FILE[f"{currency}_RUB"] = {
                    "rate": rate_float,
                    "ts": datetime.now(timezone.utc).isoformat(),
                }
                _save_cache(cache)

        # Если файл есть — проверяем на актуальность
        if CACHE_FILE.exists():
            load_cash_file = json.load(CACHE_FILE)
            cached_entry = load_cash_file.get(f"{currency}_RUB")
            if cached_entry is not None:
                rate = cached_entry.get("rate")
                ts_iso = cached_entry.get("ts")
                cache_time = date_parser.isoparse(ts_iso)
                now = datetime.now(timezone.utc)
                if (now - cache_time) < timedelta(hours=24):
                    return float(rate) * amount_float if rate is not None else None


        # Если курс не удалось получить — возвращаем 0.0 (без падения)
        if rate is None:
            return 0.0



        if currency == "USD":
            rate = _get_exchange_rate(currency, "RUB")

        if currency == "EUR":
            rate = _get_exchange_rate(currency, "RUB")



        return round(amount_float * rate, 2)
    except Exception:
        return 0.0
