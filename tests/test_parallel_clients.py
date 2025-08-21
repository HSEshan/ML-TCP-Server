import asyncio
import os
from collections import defaultdict

import pytest

from src.config import config
from src.protocol import Protocol
from tests.conftest import HOST, PORT


@pytest.mark.asyncio
async def test_parallel_clients(tcp_server):
    INTERVAL = 0.01
    NUM_CLIENTS = 10

    results = defaultdict(list)

    async def client_task(id: int):
        count = id * 10
        reader, writer = await asyncio.open_connection(HOST, PORT)

        while count > 0:

            payload = os.urandom(128)

            writer.write(Protocol.pack_message(payload))
            await writer.drain()

            length_bytes = await reader.readexactly(config.length_field_size)
            payload_length = Protocol.unpack_length(length_bytes)

            response_bytes = await reader.readexactly(payload_length)
            results[id].append(response_bytes.decode("ascii"))

            await asyncio.sleep(INTERVAL)
            count -= 1

    tasks = []
    for i in range(NUM_CLIENTS):
        tasks.append(asyncio.create_task(client_task(i + 1)))

    await asyncio.gather(*tasks)

    assert len(results) == NUM_CLIENTS
    for i in range(NUM_CLIENTS):
        assert len(results[i + 1]) == (i + 1) * 10
