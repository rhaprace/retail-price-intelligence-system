import sys
import os
from pathlib import Path
from loguru import logger

logger.remove()

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_DIR = os.getenv('LOG_DIR', 'logs')

Path(LOG_DIR).mkdir(exist_ok=True)

logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
)

logger.add(
    f"{LOG_DIR}/app.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
)

logger.add(
    f"{LOG_DIR}/error.log",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    backtrace=True,
    diagnose=True,
)

logger.add(
    f"{LOG_DIR}/scraping.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    rotation="10 MB",
    retention="14 days",
    filter=lambda record: "scraping" in record["extra"],
)

logger.add(
    f"{LOG_DIR}/api.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    rotation="10 MB",
    retention="14 days",
    filter=lambda record: "api" in record["extra"],
)


def get_logger(name: str = None):
    if name:
        return logger.bind(name=name)
    return logger


def get_scraping_logger():
    return logger.bind(scraping=True)


def get_api_logger():
    return logger.bind(api=True)


class LoggerMiddleware:
    
    def __init__(self, app):
        self.app = app
        self.logger = get_api_logger()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            import time
            start_time = time.time()
            
            await self.app(scope, receive, send)
            
            process_time = time.time() - start_time
            self.logger.info(
                f"{scope['method']} {scope['path']} - {process_time:.3f}s"
            )
        else:
            await self.app(scope, receive, send)


__all__ = ['logger', 'get_logger', 'get_scraping_logger', 'get_api_logger', 'LoggerMiddleware']
