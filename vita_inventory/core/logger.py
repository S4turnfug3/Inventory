"""
Logging-System für Vita Inventory.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Logs-Verzeichnis erstellen
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Log-Formate
SIMPLE_FORMAT = "%(levelname)-8s | %(name)s | %(message)s"
DETAILED_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
FILE_FORMAT = "[%(asctime)s] %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"


class ColoredFormatter(logging.Formatter):
    """Farbige Konsolen-Ausgabe."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Grün
        'WARNING': '\033[33m',    # Gelb
        'ERROR': '\033[31m',      # Rot
        'CRITICAL': '\033[41m',   # Rot Background
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if sys.platform == 'win32':
            # Windows: Keine Farben
            return super().format(record)
        
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str,
    level: int = logging.INFO,
    debug: bool = False,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Initialisiert einen Logger mit Konsolen- und Datei-Handler.
    
    Args:
        name: Logger-Name (üblicherweise __name__)
        level: Log-Level
        debug: Debug-Modus aktivieren
        log_file: Optionaler Dateipfad für Logs
    
    Returns:
        Konfigurierter Logger
    """
    logger = logging.getLogger(name)
    
    # Nur konfigurieren wenn noch nicht passiert
    if logger.handlers:
        return logger
    
    if debug:
        level = logging.DEBUG
    
    logger.setLevel(level)
    
    # Konsolen-Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        DETAILED_FORMAT if debug else SIMPLE_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Datei-Handler
    if log_file is None:
        log_file = LOGS_DIR / f"vita_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Immer alles in Datei
        file_formatter = logging.Formatter(FILE_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Konnte Log-Datei nicht erstellen: {e}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Gibt einen existierenden Logger zurück."""
    return logging.getLogger(name)


class PerformanceLogger:
    """Context Manager zum Loggen von Execution-Zeit."""
    
    def __init__(self, logger: logging.Logger, message: str, level: int = logging.INFO):
        self.logger = logger
        self.message = message
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(self.level, f"START: {self.message}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        if exc_type:
            self.logger.error(f"FAILED: {self.message} ({duration:.2f}s) - {exc_val}")
        else:
            self.logger.log(self.level, f"DONE: {self.message} ({duration:.2f}s)")
