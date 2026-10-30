# src/utils.py
"""
Этот модуль содержит функции для работы с JSON-файлами транзакций
и конвертации валют.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from src.constants import API_URL


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает список транзакций из JSON-файла.

    Возвращает пустой список [], если:
      - файл не найден;
      - файл пустой или невалидный JSON;
      - содержимое не является списком;
      - элементы списка не являются словарями.
    """
    path = Path(file_path)

    # Если файла нет — возвращаем пустой список (не None!)
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError, UnicodeDecodeError:
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
    Получает курс валюты через Exchange Rates Data API.

    Возвращает курс (сколько target_currency за 1 base_currency) или None при ошибке.
    """
    api_key = os.getenv("EXCHANGE_RATES_API_KEY")
    if not api_key:
        return None

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

        return float(rate)
    except Exception:
        # В продакшене лучше логировать ошибку
        return None


def normalize_transaction(tx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Приводит транзакцию из сложной структуры JSON к плоскому виду,
    ожидаемому функцией convert_transaction_to_rub.
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
    Конвертирует сумму транзакции в рубли.

    Возвращает 0.0, если конвертация невозможна.
    """
    amount = transaction.get("amount")
    currency = (transaction.get("currency") or "").upper()

    if amount is None or not isinstance(amount, (int, float)):
        return 0.0

    amount_float = float(amount)

    if currency == "RUB":
        return amount_float

    rate = _get_exchange_rate(currency, "RUB")

    if rate is None:
        return 0.0

    return amount_float * rate
