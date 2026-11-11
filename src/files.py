# src/files.py для считывания CSV и Excel файлов

from typing import Any, Dict, List, cast

import pandas as pd


def df_to_transactions(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Преобразует DataFrame в список словарей с записями транзакций.

    Пустые (NaN) значения заменяются на None.

    Args:
        df: DataFrame с данными о финансовых операциях.

    Returns:
        Список словарей, где каждый словарь — одна транзакция
        (ключи — названия колонок, значения — данные строки).

    """
    df = df.where(pd.notna(df), None)
    return cast(List[Dict[str, Any]], df.to_dict(orient="records"))


def reading_transactions_csv(file_csv: str) -> List[Dict[str, Any]]:
    """Считывает финансовые операции из CSV-файла.

    Args:
        file_csv: путь к CSV-файлу с разделителем ';'.

    Returns:
        Список словарей с транзакциями. Пустые значения — None.

    """
    return df_to_transactions(pd.read_csv(file_csv, sep=";"))


def reading_transactions_xlsx(file_xlsx: str) -> List[Dict[str, Any]]:
    """Считывает финансовые операции из Excel-файла.

    Args:
        file_xlsx: путь к файлу формата .xlsx.

    Returns:
        Список словарей с транзакциями. Пустые значения — None.

    """
    return df_to_transactions(pd.read_excel(file_xlsx))
