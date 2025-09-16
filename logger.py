import logging
from pathlib import Path
import csv
from datetime import datetime

from constants import LOG_DIR


def setup_global_logger_settings():
    # Create logs directory if it doesn't exist
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging():
    """Настройка основного логгера для общих сообщений"""
    # Создаем отдельный логгер для общих сообщений
    logger = logging.getLogger("main_logger")
    logger.setLevel(logging.INFO)

    # Очищаем существующие обработчики, если есть
    logger.handlers.clear()

    # Форматтер для общих логов
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    log_file = LOG_DIR / "application.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Предотвращаем передачу сообщений корневому логгеру
    logger.propagate = False

    return logger


def setup_model_logging():
    """Настройка логгера для записи взаимодействий с моделью в CSV формате"""
    logger = logging.getLogger("model_logger")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # CSV файл (оставляем как есть)
    csv_file = LOG_DIR / "model_interactions.csv"
    if not csv_file.exists():
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Time', 'TgNickname', 'Prompt', 'Response', 'Blocked'])

    class CSVHandler(logging.Handler):
        def emit(self, record):
            if isinstance(record.msg, dict):
                try:
                    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            record.msg.get('Time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                            record.msg.get('TgNickname', ''),
                            record.msg.get('Prompt', ''),
                            record.msg.get('Response', ''),
                            record.msg.get('Blocked', '')
                        ])
                except Exception as e:
                    print(f"Error writing to CSV: {e}")

    csv_handler = CSVHandler()
    logger.addHandler(csv_handler)

    # ДОБАВЬТЕ ЭТОТ ОБРАБОТЧИК для вывода в stdout в читаемом формате
    class StdoutHandler(logging.Handler):
        def emit(self, record):
            if isinstance(record.msg, dict):
                msg_data = record.msg
                print(f"MODEL INTERACTION: "
                      f"User: {msg_data.get('TgNickname', 'N/A')}, "
                      f"Prompt: {msg_data.get('Prompt', '')}, "
                      f"Response: {msg_data.get('Response', '')}, "
                      f"Blocked: {msg_data.get('Blocked', '')}")

    stdout_handler = StdoutHandler()
    logger.addHandler(stdout_handler)

    logger.propagate = False
    return logger


# Инициализация логгеров
setup_global_logger_settings()
logger = setup_logging()
model_logger = setup_model_logging()


# Функция-помощник для удобного логирования взаимодействий с моделью
def log_model_interaction(tg_nickname: str, prompt: str, response: str, blocked: bool):
    """Логирует взаимодействие с моделью в CSV формате"""
    model_logger.info({
        'Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'TgNickname': tg_nickname,
        'Prompt': prompt[:100],
        'Response': response[:100],
        'Blocked': blocked
    })
