import asyncio
import uvicorn

import logging
import sys
from src.core.config import settings

from src.app import create_app

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from src.dishka_provider import AppProvider

def setup_logging():
    """Настройка логирования"""

    logging.basicConfig(
        level=settings.get_log_level(),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),  # В консоль
            logging.FileHandler(settings.LOG_FILE, encoding='utf-8')  # В файл
        ]
    )


setup_logging()
app = create_app()

container = make_async_container(AppProvider())
setup_dishka(container, app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
