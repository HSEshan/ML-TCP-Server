import random
from typing import override

import pytest_asyncio

from src.config import config
from src.metrics_v2 import Metrics
from src.ml_interface_abstract import ML_Interface_Abstract
from src.protocol import Protocol
from src.tcp_server import TCP_Server

HOST = "127.0.0.1"
PORT = 9000

DUMMY_COMMANDS = [b"FD005", b"TR030", b"AS000"]


class InferenceException(Exception):
    pass


class MockMLInterface(ML_Interface_Abstract):
    def __init__(self):
        pass

    @override
    def run_inference(self, payload: bytes) -> bytes:
        random_command = random.choice(DUMMY_COMMANDS)
        return random_command

    @override
    async def async_run_inference(self, payload: bytes) -> bytes:
        return b"XXXXX"


class MockMLInterfaceWithException(ML_Interface_Abstract):
    def __init__(self):
        pass

    @override
    def run_inference(self, payload: bytes) -> bytes:
        raise InferenceException("Inference failed")


@pytest_asyncio.fixture(scope="function")
async def tcp_server():
    metrics = Metrics()
    server = TCP_Server(
        host=HOST,
        port=PORT,
        length_field_size=config.length_field_size,
        response_size=config.response_size,
        max_connections=config.max_connections,
        max_payload_size=config.max_payload_size_kb * 1024,
        payload_timeout_seconds=config.payload_timeout_seconds,
        protocol=Protocol(),
        ml_interface=MockMLInterface(),
        metrics=metrics,
    )
    await server.startup()
    yield server
    await server.shutdown()
