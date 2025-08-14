import asyncio
import os

from src.config import Config
from src.protocol import Protocol

HOST = "127.0.0.1"
PORT = 9000
INTERVAL = 0.333


async def main():
    reader, writer = await asyncio.open_connection(HOST, PORT)

    while True:

        payload = os.urandom(128)

        writer.write(Protocol.pack_message(payload))
        await writer.drain()

        length_bytes = await reader.readexactly(Config.length_field_size)
        payload_length = Protocol.unpack_length(length_bytes)

        response_bytes = await reader.readexactly(payload_length)
        print(response_bytes.decode("ascii"))

        await asyncio.sleep(INTERVAL)


asyncio.run(main())
