import asyncio
import os

import pytest

from src.config import Config
from src.protocol import Protocol

HOST = "127.0.0.1"
PORT = 9000


@pytest.mark.asyncio
async def test_tcp_client():
    """Test TCP client.
    Start TCP server before running this test.
    """
    reader, writer = await asyncio.open_connection(HOST, PORT)

    payload = os.urandom(128)

    writer.write(Protocol.pack_message(payload))
    await writer.drain()
    assert len(payload) == 128

    length_bytes = await reader.readexactly(Config.length_field_size)
    payload_length = Protocol.unpack_length(length_bytes)

    response_bytes = await reader.readexactly(payload_length)
    assert response_bytes is not None
    assert len(response_bytes) == Config.response_size

    writer.close()
    await writer.wait_closed()
