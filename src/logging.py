import logging

from config import Config


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=Config.log_level,
    )
