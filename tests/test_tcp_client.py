import asyncio
import os

import pytest
import pytest_asyncio

from src.config import Config
from src.protocol import Protocol
from src.tcp_server import TCP_Server
from tests.conftest import MockMLInterface

HOST = "127.0.0.1"
PORT = 9000


@pytest_asyncio.fixture(scope="function")
async def tcp_server():
    server = TCP_Server(HOST, PORT, Config.length_field_size, Config.response_size)
    server.ml_interface = MockMLInterface()
    server.protocol = Protocol()
    await server.startup()
    yield server
    await server.shutdown()


@pytest.mark.asyncio
async def test_tcp_client(tcp_server):
    reader, writer = await asyncio.open_connection(HOST, PORT)

    payload = os.urandom(128)

    writer.write(Protocol.pack_message(payload))
    await writer.drain()
    assert len(payload) == 128

    length_bytes = await reader.readexactly(Config.length_field_size)
    payload_length = Protocol.unpack_length(length_bytes)

    response_bytes = await reader.readexactly(payload_length)
    assert response_bytes is not None
    print(response_bytes.decode("ascii"))
    assert len(response_bytes) == Config.response_size

    writer.close()
    await writer.wait_closed()
