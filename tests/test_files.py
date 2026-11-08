import pandas as pd
import pytest

from src.files import df_to_transactions, reading_transactions_csv, reading_transactions_xlsx

""" Тесты для CSV """


def test_reading_transactions_csv(tmp_path):
    """Обычный файл: данные читаются, типы корректны."""
    file = tmp_path / "transactions.csv"
    file.write_text("id;amount;description\n1;100.5;Перевод\n2;250;Оплата\n", encoding="utf-8")

    result = reading_transactions_csv(str(file))

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["amount"] == 100.5
    assert result[1]["description"] == "Оплата"


def test_reading_transactions_csv_empty(tmp_path):
    """Пустой файл (нет даже заголовка) — ожидаем ошибку pandas."""
    file = tmp_path / "empty.csv"
    file.write_text("", encoding="utf-8")

    with pytest.raises(pd.errors.EmptyDataError):
        reading_transactions_csv(str(file))


def test_reading_transactions_csv_wrong_sep(tmp_path):
    """Файл с запятой вместо точки с запятой — вся строка уйдёт в одну колонку."""
    file = tmp_path / "wrong_sep.csv"
    file.write_text("id,amount\n1,100\n", encoding="utf-8")

    result = reading_transactions_csv(str(file))

    # pandas прочитает заголовок как единое имя колонки
    assert list(result[0].keys()) == ["id,amount"]


""" Тесты для Excel """


def test_reading_transactions_xlsx(tmp_path):
    """Готовим xlsx через pandas и проверяем чтение."""
    df = pd.DataFrame({"id": [1, 2], "amount": [100.5, 250.0]})
    file = tmp_path / "transactions.xlsx"
    df.to_excel(file, index=False)

    result = reading_transactions_xlsx(str(file))

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["amount"] == 250.0


def test_reading_transactions_xlsx_empty(tmp_path):
    """Пустой xlsx (без заголовка) — пустой список."""
    file = tmp_path / "empty.xlsx"
    pd.DataFrame().to_excel(file, index=False)

    result = reading_transactions_xlsx(str(file))
    assert result == []


def test_reading_transactions_xlsx_corrupted(tmp_path):
    file = tmp_path / "corrupted.xlsx"
    file.write_bytes(b"")

    with pytest.raises(Exception):
        reading_transactions_xlsx(str(file))


""" Тесты для NaN """


def test_transactions_with_nan(tmp_path):
    """Пропущенные значения превращаются в NaN, а не в None — это важно проверить явно."""
    file = tmp_path / "with_nan.csv"
    file.write_text("id;amount;description\n1;;Перевод\n", encoding="utf-8")

    result = reading_transactions_csv(str(file))

    value = result[0]["amount"]
    assert pd.isna(value)          # это NaN
    assert value is not None       # но это НЕ None — типичная ловушка


""" Тест для df_to_transactions """


def test_df_to_transactions():
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    result = df_to_transactions(df)

    assert result == [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
