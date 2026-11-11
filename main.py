from src import files, filter, generators, processing, utils, widget

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
    user_defined_file = input("Пункт меню: ").strip()

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
    user_defined_status = input("Статус: ").strip()

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
            f"""
Статус операции "{user_defined_status}" недоступен.

Введите статус, по которому необходимо выполнить фильтрацию.
Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING
"""
        )

print("\nОтсортировать операции по дате? Да/Нет")
user_defined_date = ""
while user_defined_date.upper() not in ["ДА", "НЕТ"]:
    user_defined_date = input("Сортировать: ").strip()
    if user_defined_date.upper() == "ДА":
        print("\nОтсортировать 'по возрастанию' или 'по убыванию'?")
        user_defined_bearings = ""
        while user_defined_bearings.lower() not in ["по возрастанию", "по убыванию"]:
            user_defined_bearings = input("Сортировать: ").strip()
            if user_defined_bearings.lower() == "по возрастанию":
                list_transaction_sorted_date = processing.sort_by_date(list_transaction_status, False)
            elif user_defined_bearings.lower() == "по убыванию":
                list_transaction_sorted_date = processing.sort_by_date(list_transaction_status, True)
            else:
                print("Некорректный ответ, попробуйте еще раз")
    elif user_defined_date.upper() == "НЕТ":
        list_transaction_sorted_date = list_transaction_status
    else:
        print("Некорректный ответ, попробуйте еще раз")

print("\nВыводить только рублевые транзакции? Да/Нет")
user_defined_currency = ""
while user_defined_currency.lower() not in ["да", "нет"]:
    user_defined_currency = input("Выводить: ").strip()
    if user_defined_currency.lower() == "да":
        list_transaction_currency = list(generators.filter_by_currency(list_transaction_sorted_date, "RUB"))
    elif user_defined_currency.lower() == "нет":
        list_transaction_currency = list_transaction_sorted_date
    else:
        print("Некорректный ответ, попробуйте еще раз")

print("\nОтфильтровать список транзакций по определенному слову в описании? Да/Нет")
user_defined_word_filter = ""
while user_defined_word_filter.lower() not in ["да", "нет"]:
    user_defined_word_filter = input("Фильтровать: ").strip()

    if user_defined_word_filter.lower() == "да":
        user_defined_word = input("Введите слово: ").strip()
        list_transaction_description = filter.process_bank_search(
            list_transaction_currency, user_defined_word)
    elif user_defined_word_filter.lower() == "нет":
        list_transaction_description = list_transaction_currency
    else:
        print("Некорректный ответ, попробуйте еще раз")

print(
    f"""
Распечатываю итоговый список транзакций...

Всего банковских операций в выборке: {len(list_transaction_description)}
"""
)

if not list_transaction_description:
    print("Транзакции не найдены.")
else:
    for item in list_transaction_description:
        print()

        # Дата и описание
        print(f"{widget.get_date(item.get('date'))} "
              f"{item.get('description') or 'Без описания'}")

        # Отправитель/получатель — одна ветка на все случаи
        masked_sender = "[Не указано]"
        sender_from = item.get("from")
        sender_to = item.get("to")

        if widget.has_value(sender_from) and widget.has_value(sender_to):
            masked_sender = (
                f"{widget.mask_account_card(sender_from)} -> "
                f"{widget.mask_account_card(sender_to)}"
            )
        elif widget.has_value(sender_from):
            masked_sender = widget.mask_account_card(sender_from)
        elif widget.has_value(sender_to):
            masked_sender = widget.mask_account_card(sender_to)

        print(masked_sender)

        # Сумма и валюта (работает и с CSV, и с JSON)
        amount, currency = utils.get_amount_info(item)
        if amount is not None and currency:
            try:
                formatted_amount = f"{float(amount):,.2f}".replace(",", " ").replace(".", ",")
            except (ValueError, TypeError):
                formatted_amount = str(amount)
            print(f"Сумма: {formatted_amount} {currency}")
        else:
            print("Сумма: данные отсутствуют")
