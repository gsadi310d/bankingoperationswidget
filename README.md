# BankingOperationsWidget

Учебный проект серверной части виджета банковских операций.  
Проект реализует функционал отображения операций клиента с поддержкой фильтрации, сортировки и маскирования чувствительных данных.  
На текущий момент проект находится в стадии активной разработки; реализован частичный функционал.

---

## Стек технологий и инструменты

- **Язык программирования**: Python 3.12
- **Управление зависимостями и окружением**: Poetry (`poetry.lock`, `pyproject.toml`)
- **Тестирование**: pytest, покрытие тестами 100% (pytest + coverage)
- **Статическая проверка типов**: mypy
- **Среда разработки**: PyCharm
- **Соблюдение стандартов качества кода** (flake8, black, isort).

---

## Установка и настройка окружения
1. Клонируйте репозиторий:
    ```
    git clone https://github.com/gsadi310d/bankingoperations…
    ```

2. Установите зависимости и инициализируйте виртуальное окружение (Для корректной работы проекта требуется установленный Poetry.):

   ```
   poetry install
   ```

## Тестирование

Для запуска тестов используется pytest. Прямой запуск файлов через python не рекомендуется: это нарушает работу фикстур, плагинов и изолированного окружения.

## Запуск тестов и покрытие
```
poetry run pytest
poetry run pytest --cov=src --cov-report=term-missing
poetry run pytest --cov=src --cov-report=html
```

## Статический анализ кода

Проверка соответствия аннотированным типам выполняется с помощью mypy:

    mypy .

Рекомендуется выполнять проверку типов перед каждым коммитом.

## Проверка стиля кода
```
poetry run flake8 .
poetry run black --check .
poetry run isort --check-only .
```

## Автоматическое исправление стиля
```
poetry run black .
poetry run isort .
```

---

## Реализованный функционал

В рамках текущей версии проекта реализованы следующие функциональные модули и утилиты:

- src/processing.py
  - filter_by_state(operations: list, state: str) -> list — фильтрация списка операций по статусу.
  - sort_by_date(operations: list) -> list — сортировка операций по дате с использованием вспомогательной функции парсинга даты (key=parse_date).

- src/masks.py
  - get_mask_card_number(card_number: str) -> str — маскирование номера банковской карты.
  - get_mask_account(account_number: str) -> str — маскирование номера счёта.

- src/common.py
  - find_first_digit_position(argument: str) -> int — поиск индекса первого вхождения цифры
  - find_first_alpha_position(argument: str) -> int — поиск индекса первого вхождения буквы
  - find_space_position(argument: str) -> int — поиск индекса первого вхождения пробела
- src/decorators.py
  - def log(filename: Optional[str] = None) -> Callable: — декоратор для логирования начала, конца и результата работы функции
- src/widget.py
  - Основная логика виджета, агрегация данных и подготовка к отображению.
  - valid_prefix(in_argument: str) -> str | None — Проверяет, начинается ли строка с одного из VALID_CARD_PREFIXES
  - mask_account_card(in_argument: str) -> str — Обрабатывает строку с префиксом и номером (карты или счёта) и возвращает
    замаскированный номер либо сообщение об ошибке
  - get_date(date_string: str) -> str — конвертация строки даты из формата ISO с микросекундами ("2024-03-11T02:26:18.671407") в формат "ДД.ММ.ГГГГ" ("11.03.2024").

- src/generators
  - filter_by_currency(transactions: Iterable[Dict[str, Any]], currency_code: str) -> Iterator[Dict[str, Any]] —  
      Возвращает итератор транзакций, валюта которых совпадает с указанной (регистронезависимо).
  - transaction_descriptions(transactions: Iterable[Dict[str, Any]]) -> Iterator[str] —
      Возвращает итератор описаний операций (description). Если описание отсутствует или пусто — возвращает "Без описания".
  - card_number_generator(start: int, end: int) -> Iterator[str] —
      Генерирует номера банковских карт в формате XXXX XXXX XXXX XXXX в заданном числовом диапазоне.

- src/utils
  - load_transactions(file_path: str) -> List[Dict[str, Any]] — Загружает список транзакций из JSON-файла  
  - _get_exchange_rate(base_currency: str, target_currency: str) -> Optional[float] — Получает курс валюты через Exchange Rates Data API.
      Возвращает итератор описаний операций (description). Если описание отсутствует или пусто — возвращает "Без описания".
  - normalize_transaction(tx: Dict[str, Any]) -> Dict[str, Any] —  Приводит транзакцию из сложной структуры JSON к плоскому виду.


---

## Структура проекта
```
.
├── src/
│   ├── __init__.py
│   ├── constanse.py       # константы
│   ├── widget.py          # основная логика виджета
│   ├── processing.py      # фильтрация и сортировка
│   ├── masks.py           # маскирование данных
│   ├── decorators.py      # содержит декораторы
│   ├── generators.py      # набор генераторов для обработки данных транзакций 
│   ├── utils.py           # функции для работы с JSON-файлами транзакций и конвертации валют 
│   └── common.py          # общие утилиты
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # фикстуры тестов
│   ├── test_decorators.py      # тесты декораторов
│   ├── test_generators.py      # тесты генераторов
│   ├── test_common.py          # тесты поиска индексов
│   ├── test_masks.py           # тесты маскирования
│   ├── test_widget.py          # тесты маскировани и работы с датами
│   ├── test_utils.py           # тесты проверки json-файлов и конвертации валюты 
│   └── test_processing.py      # тесты фильтрации и сортировки
├── pyproject.toml         # конфигурация Poetry и метаданные проекта
├── poetry.lock            # зафиксированные версии зависимостей
└── README.md              # текущая документация

```
--------------------------------------------------------------------------------

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
   - feat: add get_date utility
   - fix: resolve merge conflict in src/__init__.py
   - test: add coverage for filter_by_state edge cases
8. Отправьте Pull Request для ревью.

## Лицензия

Учебный проект. Код предоставлен в образовательных целях.


