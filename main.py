# src/main.py

from typing import Any, Dict, List

from dotenv import load_dotenv

from src import utils

load_dotenv()


def calculate_total_executed_amount(transactions: List[Dict[str, Any]]) -> float:
    """
    Вычисляет общую сумму всех выполненных (EXECUTED) транзакций в рублях.
    """
    total = 0.0

    for tx in transactions:
        if tx.get("state") != "EXECUTED":
            continue

        normalized = utils.normalize_transaction(tx)
        rub_amount = utils.convert_transaction_to_rub(normalized)

        total += rub_amount

    return round(total, 2)


print(utils._get_exchange_rate("USD", "RUB"))
print(utils._get_exchange_rate("EUR", "RUB"))

file_json = utils.load_transactions("data/operations.json")
# print(file_json)
norm_file_json = utils.normalize_transaction(file_json[1])
print(norm_file_json)

result_convert = utils.convert_transaction_to_rub(norm_file_json)
print(result_convert)

print(calculate_total_executed_amount(file_json))
