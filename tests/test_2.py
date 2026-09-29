"""Модуль проверки функций widget.py"""

import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import widget

test_iso_checklist = [
    # --- Позитивные сценарии (валидные данные) ---
    {"id": "valid_time_only", "input": "14:30:15", "expected": "success", "description": "Базовое время без даты"},
    {"id": "valid_with_ms", "input": "03:15:00.999", "expected": "success", "description": "Время с миллисекундами"},
    {
        "id": "valid_extended",
        "input": "2023-10-25T14:30:15",
        "expected": "success",
        "description": "Дата + время (расширенный формат)",
    },
    {
        "id": "valid_microseconds",
        "input": "2023-10-25T14:30:15.123456",
        "expected": "success",
        "description": "Дата + время + микросекунды",
    },
    {
        "id": "valid_offset_plus",
        "input": "2023-10-25T14:30:15+03:00",
        "expected": "success",
        "description": "Смещение часового пояса (+03:00)",
    },
    {
        "id": "valid_offset_minus",
        "input": "2023-10-25T14:30:15-05:00",
        "expected": "success",
        "description": "Отрицательное смещение (-05:00)",
    },
    {
        "id": "valid_utc_z",
        "input": "2023-10-25T14:30:15Z",
        "expected": "success_if_using_isoparse",
        "description": "UTC с маркером Z (требует dateutil.parser.isoparse)",
    },
    {
        "id": "valid_leap_year",
        "input": "2024-02-29T12:00:00",
        "expected": "success",
        "description": "Високосный год (29 февраля)",
    },
    # --- Негативные сценарии (невалидные данные) ---
    {
        "id": "invalid_month_13",
        "input": "2023-13-01T12:00:00",
        "expected": "ValueError",
        "description": "Несуществующий месяц (13)",
    },
    {
        "id": "invalid_day_feb",
        "input": "2023-02-30T00:00:00",
        "expected": "ValueError",
        "description": "Несуществующий день (30 февраля)",
    },
    {
        "id": "invalid_hour_24",
        "input": "2023-10-25T24:00:00",
        "expected": "ValueError",
        "description": "Час вне диапазона (24)",
    },
    {
        "id": "invalid_double_dot",
        "input": "2023-10-25T14:30:15.123.456",
        "expected": "ValueError",
        "description": "Две точки в долях секунды",
    },
    {
        "id": "invalid_offset_and_z",
        "input": "2023-10-25T14:30:15+03:00Z",
        "expected": "ValueError_or_custom_error",
        "description": "Одновременно смещение и Z",
    },
    {
        "id": "invalid_slashes",
        "input": "2023/10/25T14:30:15",
        "expected": "ValueError",
        "description": "Нестандартные разделители (слэши)",
    },
    {
        "id": "invalid_missing_seconds",
        "input": "2023-10-25T14:30",
        "expected": "ValueError_if_required",
        "description": "Пропущены секунды (зависит от требований)",
    },
    {
        "id": "invalid_empty_after_t",
        "input": "2023-10-25T",
        "expected": "ValueError",
        "description": "Пустое время после T",
    },
    {
        "id": "invalid_extra_chars",
        "input": "2023-10-25T14:30:15abc",
        "expected": "ValueError",
        "description": "Лишние символы в конце",
    },
    # --- Граничные и особые случаи ---
    {
        "id": "boundary_midnight_transition",
        "input": "2023-10-25T23:59:59.999999",
        "expected": "success",
        "description": "Переход через полночь (граничная секунда)",
    },
    {
        "id": "None value",
        "input": None,
        "expected": "all_success",
        "description": "Разные уровни точности долей секунды",
    },
    {
        "id": "Not correct",
        "input": 1234,
        "expected": "custom_handling_required",
        "description": "Обработка null и пустых строк",
    },
]

test_list = [
    "Maestro 1596837868705199",
    "Счет 64686473678894779589",
    "MasterCard 7158300734726758",
    "Счет 35383033474447895560",
    "Visa Classic 6831982476737658",
    "Visa Platinum 8990922113665229",
    "Visa Gold 5999414228426353",
    "Счет 73654108430135874305",
]

for test_element in test_list:
    print(widget.mask_account_card(test_element))

for test_element in test_iso_checklist:
    print(widget.get_date(test_element["input"]))
