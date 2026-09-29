"""Модуль проверки функций processing.py"""

import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import processing

data = [
    {'id': 414288290, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
    {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
    {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
    {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'},
]

# Фильтрация по умолчанию (EXECUTED)
executed_only = processing.filter_by_state(data)
print(executed_only)
# [{'id': 414288290, 'state': 'EXECUTED', ...}, {'id': 939719570, 'state': 'EXECUTED', ...}]

# Фильтрация по CANCELED
canceled_only = processing.filter_by_state(data, 'CANCELED')
print(canceled_only)
# [{'id': 594226727, 'state': 'CANCELED', ...}, {'id': 615064591, 'state': 'CANCELED', ...}]