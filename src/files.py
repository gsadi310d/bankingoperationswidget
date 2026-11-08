import pandas as pd
from typing import List, Dict, Any


def df_to_transactions(df: pd.DataFrame) -> List[Dict[str, Any]]:
    df = df.where(pd.notna(df), None)
    return df.to_dict(orient="records")


def reading_transactions_csv(file_csv: str) -> List[Dict[str, Any]]:
    return df_to_transactions(pd.read_csv(file_csv, sep=";"))


def reading_transactions_xlsx(file_xlsx: str) -> List[Dict[str, Any]]:
    return df_to_transactions(pd.read_excel(file_xlsx))
