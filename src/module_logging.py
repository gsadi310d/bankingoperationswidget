"""#module_loggiing.py модуль инициализации логгирования"""

import logging
from pathlib import Path

def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Защита от дублирования хендлеров при многократном вызове
    if logger.hasHandlers():
        return logger

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file, mode='w', encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger