# src/main.py

from dotenv import load_dotenv

from src import files, filter, masks, utils, processing,generators

load_dotenv()

print(
    """
    Привет! Добро пожаловать в программу работы с банковскими транзакциями. 
    
    Выберите необходимый пункт меню:
    
    1. Получить информацию о транзакциях из JSON-файла
    2. Получить информацию о транзакциях из CSV-файла
    3. Получить информацию о транзакциях из XLSX-файла
    
    """
      )

user_defined_file = "0"
while user_defined_file not in ["1", "2", "3"]:
    user_defined_file = input("Пункт меню: ")

    if user_defined_file == "1":
        list_transaction = utils.load_transactions("data/operations.json")
        print("Для обработки выбран JSON-файл")
    elif user_defined_file == "2":
        list_transaction = files.reading_transactions_csv("data/transactions.csv")
        print("Для обработки выбран CSV-файл")
    elif user_defined_file == "3":
        list_transaction = files.reading_transactions_xlsx("data/transactions_excel.xlsx")
        print("Для обработки выбран XLSX-файл")
    else:
        print("Для обработки выбран некорректный номер меню, попробуйте еще раз")


print(
    """
    Введите статус, по которому необходимо выполнить фильтрацию. 
    Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING

    """
      )

user_defined_status = "0"
while user_defined_status.upper() not in ["EXECUTED", "CANCELED", "PENDING"]:
    user_defined_status = input("Статус: ")

    if user_defined_status.upper() == "EXECUTED":
        list_transaction_status = processing.filter_by_state(list_transaction, "EXECUTED")
        print('Операции отфильтрованы по статусу "EXECUTED"')
    elif user_defined_status.upper() == "CANCELED":
        list_transaction_status = processing.filter_by_state(list_transaction, "CANCELED")
        print('Операции отфильтрованы по статусу "CANCELED"')
    elif user_defined_status.upper() == "PENDING":
        list_transaction_status = processing.filter_by_state(list_transaction, "PENDING")
        print('Операции отфильтрованы по статусу "PENDING"')
    else:
        print(
            f'''
            Статус операции "{user_defined_status}" недоступен.

            Введите статус, по которому необходимо выполнить фильтрацию. 
            Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING
            '''
        )


print("Отсортировать операции по дате? Да/Нет")
user_defined_date = ""
while user_defined_status.upper() not in ["ДА", "НЕТ"]:
    user_defined_date = input("Сортировать: ")
    if user_defined_status.upper() == "ДА":
        print("Отсортировать по возрастанию или по убыванию?")
        user_defined_sorted = ""
        while user_defined_sorted.lower() not in ["по возрастанию", "по убыванию"]:
            user_defined_sorted = input("Сортировать: ")
            if user_defined_sorted == "по возрастанию":
                list_transaction_sorted_date = processing.sort_by_date(list_transaction_status, False)
            elif user_defined_sorted == "по убыванию":
                list_transaction_sorted_date = processing.sort_by_date(list_transaction_status, True)
            else:
                print("Некорректный ответ, попробуйте еще раз")
    elif user_defined_status.upper() == "НЕТ":
        list_transaction_sorted_date = list_transaction_status
    else:
        print("Некорректный ответ, попробуйте еще раз")


print("Выводить только рублевые транзакции? Да/Нет")
user_defined_currency = ""
while user_defined_currency.lower() not in ["да","нет"]:
    user_defined_currency = input("Выводить: ")
    if user_defined_currency == "да":
        list_transaction_currency = list(generators.filter_by_currency(list_transaction_sorted_date, "RUB"))
    elif user_defined_currency == "нет":
        list_transaction_currency = list_transaction_sorted_date
    else:
        print("Некорректный ответ, попробуйте еще раз")


print("Отфильтровать список транзакций по определенному слову в описании? Да/Нет")
user_defined_word = ""
while user_defined_word.lower() not in ["да","нет"]:
    user_defined_word = input("Сортировать: ")
    if user_defined_word == "да":
        user_defined_word = input("Введите слово: ")
        list_transaction_description = filter.process_bank_search(list_transaction_currency, user_defined_word)
    elif user_defined_word == "нет":
        list_transaction_description = list_transaction_currency
    else:
        print("Некорректный ответ, попробуйте еще раз")


print(
    """
    Распечатываю итоговый список транзакций...

    Всего банковских операций в выборке: 
    """
)

print()

# Загружаем все транзакции (это список)
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
#
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
#
# test_csv = files.reading_transactions_csv("data/transactions.csv")
# print(test_csv[0])
# files.reading_transactions_csv("data/transactions.csv")
# test_xlsx = files.reading_transactions_xlsx("data/transactions_excel.xlsx")
# print(test_xlsx[0])
# test_search = filter.process_bank_search(test_csv, "Перевод организации")
# print(test_search[0])
# test_filter = filter.process_bank_operations(test_csv,
#                                              ["Перевод с карты на карту", 'Перевод со счета на счет'])
# print(test_filter)
