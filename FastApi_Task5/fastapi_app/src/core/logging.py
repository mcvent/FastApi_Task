import logging
import sys


def setup_logging():
    """Настройка логирования"""

    # Создаем логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Вывод в консоль (всегда)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Вывод в файл
    file_handler = logging.FileHandler('app.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()