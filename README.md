# BankingOperationsWidget

Учебный проект серверной части виджета банковских операций.
Проект реализует функционал отображения операций клиента с поддержкой фильтрации, сортировки и маскирования чувствительных данных.
На текущий момент проект находится в стадии активной разработки; реализован частичный функционал.

---

## Что нового
- Добавлен модуль `main.py` — консольный интерфейс: выбор источника данных (JSON/CSV/XLSX), фильтрация по статусу, сортировка, отбор рублёвых операций, поиск по слову в описании и итоговый вывод транзакций.
- Добавлен модуль `filter.py` для поиска и подсчёта банковских операций.
- Добавлен модуль `files.py` для считывания CSV и Excel файлов.
- Добавлен модуль `module_logging.py` для централизованной инициализации логирования.
- В `utils.py` добавлена функция `get_amount_info` — единое извлечение суммы и валюты для форматов CSV и JSON (JSON хранит их во вложенной структуре `operationAmount`).
- В `widget.py` добавлена функция `has_value` — проверка заполненности значений с учётом NaN/None из CSV.
- Логи теперь перезаписываются при каждом запуске приложения (режим `mode='w'`).
- Логгер автоматически создаёт родительские директории для файла лога.

## Стек технологий и инструментов

- Язык программирования: Python 3.14
- Управление зависимостями и окружением: Poetry (`poetry.lock`, `pyproject.toml`)
- Тестирование: pytest, покрытие тестами 100% (pytest + coverage)
- Статическая проверка типов: mypy
- Среда разработки: PyCharm
- Соблюдение стандартов качества кода: flake8, black, isort

---

## Установка и настройка окружения
1. Клонируйте репозиторий:
    git clone https://github.com/gsadi310d/bankingoperations…

2. Установите зависимости и инициализируйте виртуальное окружение (для корректной работы проекта требуется установленный Poetry):
    poetry install

## Запуск программы

    poetry run python main.py

Программа последовательно запрашивает:
1. источник данных (JSON / CSV / XLSX);
2. статус фильтрации (EXECUTED / CANCELED / PENDING);
3. необходимость сортировки по дате и её направление;
4. отбор только рублёвых транзакций;
5. ключевое слово для поиска по описанию (опционально).

По итогам выводится список транзакций с датой, замаскированными реквизитами и суммой.

## Тестирование

Для запуска тестов используется pytest. Прямой запуск файлов через python не рекомендуется: это нарушает работу фикстур, плагинов и изолированного окружения.

## Запуск тестов и покрытие
    poetry run pytest
    poetry run pytest --cov=src --cov-report=term-missing
    poetry run pytest --cov=src --cov-report=html

## Статический анализ кода

Проверка соответствия аннотированным типам выполняется с помощью mypy:

    mypy .

Рекомендуется выполнять проверку типов перед каждым коммитом.

## Проверка стиля кода
    poetry run flake8 .
    poetry run black --check .
    poetry run isort --check-only .

## Автоматическое исправление стиля
    poetry run black .
    poetry run isort .


---

## Реализованный функционал

- src/main.py
  - Точка входа: консольное меню для выбора файла, фильтрации, сортировки, отбора по валюте, поиска по описанию и вывода итогового списка.

- src/processing.py
  - filter_by_state(operations: list, state: str) -> list — фильтрация списка операций по статусу.
  - sort_by_date(operations: list, reverse: bool = True) -> list — сортировка операций по дате.

- src/masks.py
  - get_mask_card_number(card_number: str) -> str — маскирование номера банковской карты.
  - get_mask_account(account_number: str) -> str — маскирование номера счёта.

- src/common.py
  - find_first_digit_position(argument: str) -> int — поиск индекса первого вхождения цифры.
  - find_first_alpha_position(argument: str) -> int — поиск индекса первого вхождения буквы.
  - find_space_position(argument: str) -> int — поиск индекса первого вхождения пробела.

- src/decorators.py
  - log(filename: Optional[str] = None) -> Callable — декоратор для логирования начала, конца и результата работы функции.

- src/widget.py
  - Основная логика виджета, агрегация данных и подготовка к отображению.
  - valid_prefix(in_argument: str) -> str | None — возвращает наиболее длинный валидный префикс строки (карта/счёт) или None.
  - mask_account_card(in_argument: Any) -> str — обрабатывает строку с префиксом и номером (карты или счёта) и возвращает замаскированный номер либо сообщение об ошибке.
  - get_date(in_datetime: Any) -> str — конвертация строки даты из формата ISO ("2024-03-11T02:26:18.671407") в формат "ДД.ММ.ГГГГ" ("11.03.2024"); при некорректном вводе возвращает сообщение об ошибке.
  - has_value(value: Any) -> bool — проверяет, что значение заполнено и не является NaN/None из CSV.

- src/generators.py
  - filter_by_currency(transactions: Iterable[Dict[str, Any]], currency_code: str) -> Iterator[Dict[str, Any]] — возвращает итератор транзакций, валюта которых совпадает с указанной (регистронезависимо).
  - transaction_descriptions(transactions: Iterable[Dict[str, Any]]) -> Iterator[str] — возвращает итератор описаний операций; если описание отсутствует — "Без описания".
  - card_number_generator(start: int, end: int) -> Iterator[str] — генерирует номера карт в формате XXXX XXXX XXXX XXXX в заданном диапазоне.

- src/utils.py
  - load_transactions(file_path: str) -> List[Dict[str, Any]] — загружает список транзакций из JSON-файла.
  - get_amount_info(item: Dict[str, Any]) -> Tuple[Any, str] — извлекает сумму и код валюты; поддерживает и плоские поля CSV (amount, currency_code), и вложенную структуру JSON (operationAmount).

- src/external_api.py
  - convert_transaction(transaction: Dict[str, Any]) -> float — конвертирует сумму транзакции в рубли по актуальному курсу.

- src/module_logging.py
  - setup_logger(name: str, log_file: str, level: int = logging.DEBUG) — подключение модуля логирования к другому модулю.

- src/files.py
  - reading_transactions_csv(file_csv: str) -> List[Dict[str, Any]] — считывает финансовые операции из CSV-файла.
  - reading_transactions_xlsx(file_xlsx: str) -> List[Dict[str, Any]] — считывает финансовые операции из XLSX-файла.

- src/filter.py
  - process_bank_search(data: List[Dict[str, Any]], search: str) -> List[Dict[str, Any]] — возвращает операции, в описании которых есть строка поиска.
  - process_bank_operations(data: List[Dict[str, Any]], categories: List[str]) -> Dict[Any, int] — считает количество операций в каждой из заданных категорий.

---

## Структура проекта
```
.
├── data/
│   ├── operations.json
│   ├── transactions.csv
│   └── transactions_excel.xlsx
├── src/
│   ├── __init__.py
│   ├── constants.py                # константы: валидные префиксы, настройки API
│   ├── widget.py                   # основная логика виджета и вывода
│   ├── processing.py               # фильтрация и сортировка
│   ├── masks.py                    # маскирование данных
│   ├── decorators.py               # декораторы
│   ├── generators.py               # генераторы для обработки транзакций
│   ├── utils.py                    # загрузка JSON и извлечение суммы/валюты
│   ├── external_api.py             # конвертация валют
│   ├── module_logging.py           # подключение модуля логирования
│   ├── files.py                    # чтение CSV и Excel файлов
│   ├── filter.py                   # поиск и подсчёт операций
│   └── common.py                   # общие утилиты
├── main.py                         # точка входа: консольное меню
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # фикстуры тестов
│   ├── test_decorators.py          # тесты декораторов
│   ├── test_generators.py          # тесты генераторов
│   ├── test_common.py              # тесты поиска индексов
│   ├── test_masks.py              # тесты маскирования
│   ├── test_widget.py              # тесты маскирования, has_value и работы с датами
│   ├── test_utils.py               # тесты загрузки JSON и извлечения суммы
│   ├── test_files.py               # тесты чтения CSV и Excel файлов
│   ├── test_filter.py              # тесты поиска и подсчёта операций
│   ├── test_logging.py             # тесты логирования
│   ├── test_external_api.py        # тесты конвертации валюты
│   └── test_processing.py          # тесты фильтрации и сортировки
├── pyproject.toml                  # конфигурация Poetry и метаданные проекта
├── poetry.lock                     # зафиксированные версии зависимостей
└── README.md                       # текущая документация
```
---

## Рекомендации по разработке и вкладу (Contributing Guidelines)

При добавлении нового функционала или исправлении ошибок рекомендуется соблюдать следующий порядок действий:

1. Создайте новую ветку на основе актуальной версии целевой ветки:
   git checkout -b feature/your-feature-name

2. Реализуйте требуемую функциональность в соответствующих модулях.
3. Напишите тесты в папке tests/, покрывающие позитивные и негативные сценарии.
4. Проверьте корректность аннотаций типов:
   mypy .

5. Запустите полный набор тестов:
   pytest

6. При наличии конфликтов слияния — разрешите их вручную, избегая автоматических стратегий, которые могут нарушить логику утилит.
7. Оформите коммит с семантическим сообщением, например:
   - feat: add get_amount_info utility
   - fix: handle NaN values in mask_account_card
   - test: add coverage for get_date edge cases
8. Отправьте Pull Request для ревью.

## Лицензия

Учебный проект. Код предоставлен в образовательных целях.