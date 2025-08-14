import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    host: str = os.getenv("HOST", "0.0.0.0")  # Default to bind all interfaces
    port: int = int(os.getenv("PORT", "9000"))  # Default port
    length_field_size: int = int(os.getenv("LENGTH_FIELD_SIZE", "4"))  # Default 4 bytes
    response_size: int = int(
        os.getenv("RESPONSE_SIZE", "1024")
    )  # Default response size
    log_level: str = os.getenv("LOG_LEVEL", "INFO")  # Default log level
    max_connections: int = int(
        os.getenv("MAX_CONNECTIONS", "100")
    )  # Default 100 connections
    max_payload_size_kb: int = int(
        os.getenv("MAX_PAYLOAD_SIZE_KB", "1024")
    )  # Default 1MB

    def __post_init__(self):
        """Validate configuration values"""
        if not (1024 <= self.port <= 65535):
            raise ValueError(f"Port must be between 1024-65535, got {self.port}")

        if self.length_field_size not in [2, 4, 8]:
            raise ValueError(
                f"Length field size must be 2, 4, or 8, got {self.length_field_size}"
            )

        if self.response_size <= 0:
            raise ValueError(
                f"Response size must be positive, got {self.response_size}"
            )

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {self.log_level}")
