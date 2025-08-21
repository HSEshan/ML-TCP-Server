import logging

import uvicorn

from src.config import config, debug_config
from src.http_server import app
from src.metrics_v2 import Metrics
from src.ml_interface import ML_Interface
from src.protocol import Protocol
from src.tcp_server import TCP_Server


def setup_tcp_server(metrics: Metrics) -> TCP_Server:
    logger = logging.getLogger(__name__)

    server = TCP_Server(
        host=config.host,
        port=config.port,
        length_field_size=config.length_field_size,
        response_size=config.response_size,
        max_connections=config.max_connections,
        max_payload_size=config.max_payload_size_kb * 1024,
        payload_timeout_seconds=config.payload_timeout_seconds,
        protocol=Protocol(),
        ml_interface=ML_Interface(),
        metrics=metrics,
    )

    logger.debug("Config: %s", debug_config())

    return server


def setup_http_server() -> uvicorn.Server:
    uvicorn_config = uvicorn.Config(app, host=config.host, port=8080, loop="asyncio")
    return uvicorn.Server(uvicorn_config)
