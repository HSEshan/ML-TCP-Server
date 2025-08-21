import asyncio
import os

from src.config import config
from src.protocol import Protocol

HOST = "127.0.0.1"
PORT = 9000
INTERVAL = 0.333
NUM_CLIENTS = 5


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
        print(f"Client {id} received response: {response_bytes.decode('ascii')}")

        await asyncio.sleep(INTERVAL)
        count -= 1


async def main():
    tasks = []
    for i in range(NUM_CLIENTS):
        tasks.append(asyncio.create_task(client_task(i + 1)))

    await asyncio.gather(*tasks)


asyncio.run(main())
