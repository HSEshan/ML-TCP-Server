import logging

from src.config import Config
from src.ml_interface import ML_Interface
from src.protocol import Protocol
from src.tcp_server import TCP_Server


def setup_tcp_server() -> TCP_Server:
    logger = logging.getLogger(__name__)

    server = TCP_Server(
        host=Config.host,
        port=Config.port,
        length_field_size=Config.length_field_size,
        response_size=Config.response_size,
        max_connections=Config.max_connections,
        max_payload_size=Config.max_payload_size_kb * 1024,
        protocol=Protocol(),
        ml_interface=ML_Interface(),
    )

    return server
