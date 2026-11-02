# src/main.py

from dotenv import load_dotenv

from src import external_api, utils

load_dotenv()

# Загружаем все транзакции (это список)
transactions = utils.load_transactions("data/operations.json")
print(transactions[1])

result = external_api.convert_transaction(transactions[1])
print(result)

# Конвертируем каждую транзакцию по отдельности
converted_results = []
for tx in transactions:
    result = external_api.convert_transaction(tx)  # tx — это один dict
    converted_results.append(result)

print(converted_results)
