# src/external_api.py
"""
Этот модуль содержит функции для конвертации валют.

Из-за ограничений API (100 запросов в месяц)
будет делаться один запрос в сутки и курс сохраняться в data/rates_cache.json
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from dateutil import parser as date_parser
from requests.exceptions import RequestException

from src.constants import API_URL, SUPPORTED_CURRENCIES

CACHE_FILE = Path("data/rates_cache.json")
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

CACHE_TTL_HOURS = 24


def convert_transaction(transaction: Dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли.

    Логика:
      - Если валюта RUB — возвращаем сумму без изменений.
      - Если валюта не в SUPPORTED_CURRENCIES — возвращаем 0.0.
      - Иначе:
          * Проверяем локальный кэш (CACHE_FILE).
          * Если кэш есть и не старше 24 часов — берём курс оттуда.
          * Иначе — запрашиваем API, обновляем кэш, возвращаем конвертированную сумму.
      - При любой ошибке (файл, API, парсинг) возвращаем 0.0.
    """

    # Валидация суммы
    op_amount = transaction.get("operationAmount")
    if not isinstance(op_amount, dict):
        return 0.0

    raw_amount = op_amount.get("amount")
    if raw_amount is None:
        return 0.0

    try:
        amount_float = float(raw_amount)
    except (TypeError, ValueError):
        return 0.0

    # Нормализация валюты
    curr_info = op_amount.get("currency")
    if not isinstance(curr_info, dict):
        return 0.0

    raw_currency = curr_info.get("code")
    if not raw_currency:
        return 0.0

    currency = str(raw_currency).strip().upper()

    # RUB — без конвертации
    if currency == "RUB":
        return round(amount_float, 2)

    # Только поддерживаемые валюты
    if currency not in SUPPORTED_CURRENCIES:
        return 0.0

    key = f"{currency}_RUB"
    rate: Optional[float] = None

    # 1. Пробуем взять из кэша
    if CACHE_FILE.exists():
        try:
            with CACHE_FILE.open("r", encoding="utf-8") as f:
                cache = json.load(f)

            entry = cache.get(key)
            if entry:
                ts_iso = entry.get("ts")
                rate_val = entry.get("rate")
                if rate_val is not None and ts_iso:
                    cache_time = date_parser.isoparse(ts_iso)
                    now = datetime.now(timezone.utc)
                    if (now - cache_time) <= timedelta(hours=CACHE_TTL_HOURS):
                        rate = float(rate_val)
        except Exception:
            # Если кэш битый или нечитаемый — игнорируем и идём к API
            rate = None

    # 2. Если кэш не подошёл — запрашиваем API и обновляем кэш
    if rate is None:
        api_key = os.getenv("EXCHANGE_RATES_API_KEY")
        if not api_key:
            return 0.0

        params = {"base": currency, "symbols": "RUB"}
        headers = {"apikey": api_key}

        try:
            resp = requests.get(API_URL, params=params, headers=headers, timeout=5)
            resp.raise_for_status()
            data = resp.json()

            rates = data.get("rates", {})
            rate_raw = rates.get("RUB")
            if rate_raw is None:
                return 0.0

            rate = float(rate_raw)

            # Обновляем кэш атомарно
            tmp_path = CACHE_FILE.with_suffix(".json.tmp")
            new_cache = {key: {"rate": rate, "ts": datetime.now(timezone.utc).isoformat()}}

            try:
                with tmp_path.open("w", encoding="utf-8") as f:
                    json.dump(new_cache, f, ensure_ascii=False, indent=2)
                os.replace(str(tmp_path), str(CACHE_FILE))
            except OSError:
                # Если не удалось сохранить кэш — всё равно возвращаем курс
                pass

        except RequestException:
            # Ошибка сети/API — возвращаем 0.0, кэш не трогаем
            return 0.0

        except (ValueError, TypeError):
            return 0.0

    return round(amount_float * rate, 2)
