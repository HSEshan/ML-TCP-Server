import asyncio
import os

import pytest

from src.config import config
from src.protocol import Protocol
from tests.conftest import HOST, PORT


@pytest.mark.asyncio
async def test_tcp_client(tcp_server):
    reader, writer = await asyncio.open_connection(HOST, PORT)

    payload = os.urandom(128)

    writer.write(Protocol.pack_message(payload))
    await writer.drain()

    try:
        length_bytes = await asyncio.wait_for(
            reader.readexactly(config.length_field_size), timeout=10
        )
        payload_length = Protocol.unpack_length(length_bytes)
    except asyncio.TimeoutError:
        pytest.fail("Timeout")

    response_bytes = await reader.readexactly(payload_length)

    writer.close()

    assert len(payload) == 128
    assert response_bytes is not None
    assert len(response_bytes) == config.response_size
