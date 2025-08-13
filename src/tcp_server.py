import asyncio
import logging

from ml_interface import ML_Interface
from protocol import Protocol

logger = logging.getLogger(__name__)


class TCP_Server:
    def __init__(
        self, host: str, port: int, length_field_size: int, response_size: int
    ):
        self.host: str = host
        self.port: int = port
        self.protocol: Protocol = Protocol()
        self.ml_interface: ML_Interface = ML_Interface()
        self.length_field_size: int = length_field_size
        self.response_size: int = response_size
        self.server: asyncio.Server | None = None

    async def start(self):
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        logger.info(f"Server started on {self.host}:{self.port}")

    async def stop(self):
        self.server.close()
        await self.server.wait_closed()

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        peer = writer.get_extra_info("peername")
        logger.info(f"Peer {peer} connected")

        try:
            while True:
                length_bytes = await reader.readexactly(self.length_field_size)
                payload_len = self.protocol.unpack_length(length_bytes)

                payload = await reader.readexactly(payload_len)
                logger.debug(f"Received {payload_len} bytes from {peer}")

                prediction = self.ml_interface.run_inference(payload)

                response = self.protocol.pack_prediction(prediction)
                writer.write(response)
                await writer.drain()
                logger.debug(f"Sent {len(response)} bytes to {peer}")

        except asyncio.IncompleteReadError:
            logger.info(f"Client {peer} disconnected.")
        except Exception as e:
            logger.error(f"Error handling {peer}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
