import asyncio
import logging

from src.config import Config
from src.logging import setup_logging
from src.ml_interface import ML_Interface
from src.protocol import Protocol
from src.tcp_server import TCP_Server


async def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    protocol = Protocol()
    ml_interface = ML_Interface()

    server = TCP_Server(
        host=Config.host,
        port=Config.port,
        length_field_size=Config.length_field_size,
        response_size=Config.response_size,
    )

    server.set_protocol(protocol)
    server.set_ml_interface(ml_interface)

    try:
        await server.startup()
    except asyncio.CancelledError:
        await server.shutdown()
        logger.info("Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
