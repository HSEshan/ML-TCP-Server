import asyncio
import logging

from src.config import config
from src.core import setup_http_server, setup_tcp_server
from src.logging import setup_logging
from src.metrics_v2 import metrics


async def main():
    setup_logging(config.log_level)
    logger = logging.getLogger(__name__)

    await metrics.start()

    tcp_server = setup_tcp_server(metrics)
    http_server = setup_http_server()

    try:
        await tcp_server.startup()
        await http_server.serve()
        async with tcp_server.server:
            await tcp_server.server.serve_forever()

    except asyncio.CancelledError:
        await tcp_server.shutdown()
        logger.info("Server stopped")
    finally:
        await metrics.stop()


if __name__ == "__main__":
    asyncio.run(main())
