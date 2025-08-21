import os
from dataclasses import asdict, dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    host: str
    port: int
    length_field_size: int
    response_size: int
    log_level: str
    max_connections: int
    max_payload_size_kb: int
    payload_timeout_seconds: int

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

        if self.payload_timeout_seconds <= 0:
            raise ValueError(
                f"Payload timeout must be positive, got {self.payload_timeout_seconds}"
            )

        if self.max_payload_size_kb <= 0:
            raise ValueError(
                f"Max payload size must be positive, got {self.max_payload_size_kb}"
            )

        if self.max_connections <= 0:
            raise ValueError(
                f"Max connections must be positive, got {self.max_connections}"
            )

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        load_dotenv()
        return cls(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "9000")),
            length_field_size=int(os.getenv("LENGTH_FIELD_SIZE", "4")),
            response_size=int(os.getenv("RESPONSE_SIZE", "1024")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_connections=int(os.getenv("MAX_CONNECTIONS", "100")),
            max_payload_size_kb=int(os.getenv("MAX_PAYLOAD_SIZE_KB", "1024")),
            payload_timeout_seconds=int(os.getenv("PAYLOAD_TIMEOUT_SECONDS", "30")),
        )

    @classmethod
    def from_ini(cls, path: str) -> "Config":
        """Load configuration from an INI file"""
        from configparser import ConfigParser

        parser = ConfigParser()
        parser.read(path)
        section = parser["config"]

        return cls(
            host=section.get("HOST", "0.0.0.0"),
            port=section.getint("PORT", 9000),
            length_field_size=section.getint("LENGTH_FIELD_SIZE", 4),
            response_size=section.getint("RESPONSE_SIZE", 1024),
            log_level=section.get("LOG_LEVEL", "INFO"),
            max_connections=section.getint("MAX_CONNECTIONS", 100),
            max_payload_size_kb=section.getint("MAX_PAYLOAD_SIZE_KB", 1024),
            payload_timeout_seconds=section.getint("PAYLOAD_TIMEOUT_SECONDS", 30),
        )


config = Config.from_env()


def debug_config() -> dict:
    return asdict(config)
