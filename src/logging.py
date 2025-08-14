import logging
import sys
from typing import Optional

from src.config import Config


def setup_logging(log_level: Optional[str] = None):
    """Setup structured logging with proper formatting"""
    level = log_level or Config.log_level

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # Setup file handler for production
    try:
        file_handler = logging.FileHandler("tcp_server.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
    except Exception as e:
        logging.warning(f"Could not setup file logging: {e}")
        file_handler = None

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    if file_handler:
        root_logger.addHandler(file_handler)

    # Set specific logger levels
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("src").setLevel(level)
