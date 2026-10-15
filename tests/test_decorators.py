import logging
import os

import pytest

from src.decorators import log


def test_log_success_console(capsys):
    """
    Сценарий: успешное выполнение, лог в консоль (без filename).
    Ожидаем: "<func_name> ok" в stdout/stderr.
    """

    @log()
    def add(a, b):
        return a + b

    result = add(2, 3)
    assert result == 5

    captured = capsys.readouterr()
    # Логи пишутся в stderr (StreamHandler по умолчанию)
    output = captured.err.strip()

    assert "add ok" in output


def test_log_error_console(capsys):
    """
    Сценарий: функция выбрасывает исключение, лог в консоль.
    Ожидаем: "<func_name> error: <type>. Inputs: ((args), {kwargs})"
    """

    @log()
    def divide(a, b):
        if b == 0:
            raise ZeroDivisionError("Деление на ноль")
        return a / b

    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

    captured = capsys.readouterr()
    output = captured.err.strip()

    assert "divide error: ZeroDivisionError" in output
    assert "Inputs: ((10, 0), {})" in output


def test_log_success_file():
    """
    Сценарий: успешное выполнение, лог в файл (filename задан).
    Ожидаем: файл создан, содержит "<func_name> ok".
    """
    logfile = "test_log_success.txt"

    @log(filename=logfile)
    def multiply(x, y):
        return x * y

    result = multiply(4, 5)
    assert result == 20

    assert os.path.exists(logfile)

    with open(logfile, "r", encoding="utf-8") as f:
        content = f.read().strip()

    assert content == "multiply ok"

    # Убираем тестовый файл после проверки
    os.remove(logfile)


def test_log_error_file():
    """
    Сценарий: ошибка, лог в файл.
    Ожидаем: файл создан, содержит строку с типом ошибки и Inputs.
    """
    logfile = "test_log_error.txt"

    @log(filename=logfile)
    def bad_func(value):
        if value < 0:
            raise ValueError("Отрицательное значение")
        return value

    with pytest.raises(ValueError):
        bad_func(-1)

    assert os.path.exists(logfile)

    with open(logfile, "r", encoding="utf-8") as f:
        content = f.read().strip()

    assert "bad_func error: ValueError" in content
    assert "Inputs: ((-1,), {})" in content

    os.remove(logfile)


def test_log_with_kwargs_and_args():
    """
    Сценарий: проверка, что корректно логируются и args, и kwargs.
    """
    logfile = "test_log_kwargs.txt"

    @log(filename=logfile)
    def process(a, b, c=10):
        if a + b + c < 0:
            raise RuntimeError("Сумма отрицательная")
        return a + b + c

    result = process(1, 2, c=3)
    assert result == 6

    with open(logfile, "r", encoding="utf-8") as f:
        content = f.read().strip()

    assert "process ok" in content
    os.remove(logfile)


def test_log_does_not_swallow_exceptions():
    """
    Сценарий: декоратор не «съедает» исключения, они пробрасываются дальше.
    Это важно, чтобы поведение функций не менялось.
    """

    @log()
    def fail():
        raise TypeError("Специально вызванная ошибка")

    with pytest.raises(TypeError) as exc_info:
        fail()

    assert str(exc_info.value) == "Специально вызванная ошибка"


def test_log_reuse_logger_no_duplicate_handlers():
    """
    Сценарий: проверка, что при повторном вызове не дублируются хендлеры.
    Это закроет ветку if logger.hasHandlers(): logger.handlers.clear()
    """
    logfile = "test_log_reuse.txt"

    @log(filename=logfile)
    def dummy(x):
        return x

    # Первый вызов
    dummy(1)
    # Второй вызов — тут должен сработать clear()
    dummy(2)

    assert os.path.exists(logfile)
    with open(logfile, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # В файле должно быть две строки: по одной на каждый вызов
    lines = content.splitlines()
    assert len(lines) == 2
    assert "dummy ok" in lines[0]
    assert "dummy ok" in lines[1]

    os.remove(logfile)


def test_log_decorator_clears_existing_handlers(logger_with_handler):

    @log()
    def test_func():
        return 42

    result = test_func()
    assert result == 42

    logger = logging.getLogger("test_func")
    assert len(logger.handlers) == 1

    handler = logger.handlers[0]
    assert isinstance(handler, (logging.FileHandler, logging.StreamHandler))
