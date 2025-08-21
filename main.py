import asyncio
import logging

from src.config import config
from src.core import setup_http_server, setup_tcp_server
from src.logging import setup_logging
from src.metrics import Metrics


async def main():
    setup_logging(config.log_level)
    logger = logging.getLogger(__name__)

    metrics = Metrics()
    tcp_server = setup_tcp_server(metrics)
    http_server = await setup_http_server(metrics)

    try:
        await tcp_server.startup()
        await http_server.start()
        async with tcp_server.server:
            await tcp_server.server.serve_forever()

    except asyncio.CancelledError:
        await tcp_server.shutdown()
        await http_server.stop()
        logger.info("Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
