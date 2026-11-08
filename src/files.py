from typing import Any, Dict, List, cast

import pandas as pd


def df_to_transactions(df: pd.DataFrame) -> List[Dict[str, Any]]:
    df = df.where(pd.notna(df), None)
    return cast(List[Dict[str, Any]], df.to_dict(orient="records"))


def reading_transactions_csv(file_csv: str) -> List[Dict[str, Any]]:
    return df_to_transactions(pd.read_csv(file_csv, sep=";"))


def reading_transactions_xlsx(file_xlsx: str) -> List[Dict[str, Any]]:
    return df_to_transactions(pd.read_excel(file_xlsx))
