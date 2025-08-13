import asyncio

from src.config import Config
from src.tcp_server import TCP_Server


async def main():
    server = TCP_Server(
        host=Config.host,
        port=Config.port,
        length_field_size=Config.length_field_size,
        response_size=Config.response_size,
    )

    await server.start()
    async with server.server:
        await server.server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
