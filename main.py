# src/main.py

from dotenv import load_dotenv

from src import masks, utils, files

load_dotenv()

# # Загружаем все транзакции (это список)
# transactions = utils.load_transactions("data/operations.json")
# print(transactions[1])
#
# result = external_api.convert_transaction(transactions[1])
# print(result)
#
# # Конвертируем каждую транзакцию по отдельности
# converted_results = []
# for tx in transactions:
#     result = external_api.convert_transaction(tx)  # tx — это один dict
#     converted_results.append(result)
#
# print(converted_results)

# print(masks.get_mask_card_number("1596837868705199"))
# print(masks.get_mask_card_number(""))
# print(masks.get_mask_card_number("15968"))
# print(masks.get_mask_card_number("1596aaa868705199"))
#
# print(masks.get_mask_account("35383033474447895560"))
# print(masks.get_mask_account(""))
# print(masks.get_mask_account("35383"))
# print(masks.get_mask_account("35383asdfg4447895560"))
#
# print(utils.load_transactions("data/operations.json"))
# print(utils.load_transactions(""))
# print(utils.load_transactions("operations.json"))
# print(utils.load_transactions("data/rates_cache.json"))

# test_csv = files.reading_transactions_csv("data/transactions.csv")
# print(test_csv[0])
# files.reading_transactions_csv("data/transactions.csv")
test_xlsx = files.reading_transactions_xlsx("data/transactions_excel.xlsx")
print(test_xlsx[0])
