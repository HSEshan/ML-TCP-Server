import asyncio
import logging

from src.config import Config
from src.core import setup_tcp_server
from src.logging import setup_logging


async def main():
    setup_logging(Config.log_level)
    logger = logging.getLogger(__name__)

    server = setup_tcp_server()

    try:
        await server.startup()
        async with server.server:
            await server.server.serve_forever()
    except asyncio.CancelledError:
        await server.shutdown()
        logger.info("Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
