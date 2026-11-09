import logging

from src.module_logging import setup_logger  # поправь путь под свой проект


def test_setup_logger_returns_logger(tmp_path):
    """Функция возвращает объект Logger с заданным именем."""
    log_file = tmp_path / "logs" / "app.log"
    logger = setup_logger("test_logger", str(log_file))

    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"


def test_setup_logger_creates_log_file(tmp_path):
    """Файл лога и родительские директории создаются автоматически."""
    log_file = tmp_path / "deep" / "nested" / "app.log"
    setup_logger("file_creator", str(log_file))

    assert log_file.exists()


def test_setup_logger_message_written(tmp_path):
    """Сообщение из logger.info попадает в файл с уровнем и временем."""
    log_file = tmp_path / "app.log"
    logger = setup_logger("writer", str(log_file))

    logger.info("Тестовое сообщение")

    content = log_file.read_text(encoding="utf-8")
    assert "Тестовое сообщение" in content
    assert "INFO" in content
    assert "writer" in content  # имя логгера из шаблона форматтера


def test_setup_logger_default_level_is_debug(tmp_path):
    """По умолчанию уровень DEBUG, поэтому debug-сообщение тоже пишется."""
    log_file = tmp_path / "debug.log"
    logger = setup_logger("debug_logger", str(log_file))

    assert logger.level == logging.DEBUG

    logger.debug("Отладочное сообщение")
    content = log_file.read_text(encoding="utf-8")
    assert "Отладочное сообщение" in content
    assert "DEBUG" in content


def test_setup_logger_custom_level(tmp_path):
    """При уровне WARNING сообщение уровня INFO не записывается."""
    log_file = tmp_path / "warn.log"
    logger = setup_logger("warn_logger", str(log_file), level=logging.WARNING)

    logger.info("Не должно попасть в лог")
    logger.warning("Должно попасть в лог")

    content = log_file.read_text(encoding="utf-8")
    assert "Должно попасть в лог" in content
    assert "Не должно попасть в лог" not in content


def test_setup_logger_no_duplicate_handlers(tmp_path):
    """Повторный вызов с тем же именем не добавляет второй хендлер."""
    log_file = tmp_path / "dup.log"

    logger1 = setup_logger("dup_logger", str(log_file))
    handlers_count = len(logger1.handlers)

    logger2 = setup_logger("dup_logger", str(log_file))

    assert logger1 is logger2
    assert len(logger2.handlers) == handlers_count  # хендлеров не стало больше


def test_setup_logger_single_handler(tmp_path):
    """У свежесозданного логгера ровно один FileHandler."""
    log_file = tmp_path / "single.log"
    logger = setup_logger("single_logger", str(log_file))

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.FileHandler)


def test_setup_logger_no_propagate(tmp_path):
    """Сообщения не должны дублироваться в root-логгер."""
    logger = setup_logger("prop_test", str(tmp_path / "p.log"))
    assert logger.propagate is False
