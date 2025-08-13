import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    host: str = os.getenv("HOST")
    port: int = os.getenv("PORT")
    length_field_size: int = os.getenv("LENGTH_FIELD_SIZE")
    response_size: int = os.getenv("RESPONSE_SIZE")
    log_level: str = os.getenv("LOG_LEVEL")
