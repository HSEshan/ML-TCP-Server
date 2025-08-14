import asyncio
import logging
from typing import Set

from src.ml_interface import ML_Interface
from src.protocol import Protocol

logger = logging.getLogger(__name__)


class TCP_Server:
    def __init__(
        self,
        host: str,
        port: int,
        length_field_size: int,
        response_size: int,
        max_connections: int,
        max_payload_size: int,
        protocol: Protocol,
        ml_interface: ML_Interface,
    ):
        self.host: str = host
        self.port: int = port
        self.protocol: Protocol = protocol
        self.ml_interface: ML_Interface = ml_interface
        self.length_field_size: int = length_field_size
        self.response_size: int = response_size
        self.server: asyncio.Server = ...
        self.running: bool = True
        self.active_connections: Set[asyncio.StreamWriter] = set()
        self.max_connections: int = max_connections
        self.max_payload_size: int = max_payload_size

    async def startup(self):
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port,
            limit=self.max_payload_size,
            backlog=50,
        )
        logger.info(f"Server started on {self.host}:{self.port}")

    async def shutdown(self):
        self.running = False
        logger.info("Shutting down server...")

        # Close all active connections
        for writer in self.active_connections.copy():
            writer.close()
            try:
                await writer.wait_closed()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")

        if self.server:
            self.server.close()
            await self.server.wait_closed()

        logger.info("Server shutdown complete")

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        peer = writer.get_extra_info("peername")

        # Check connection limit
        if len(self.active_connections) >= self.max_connections:
            logger.warning(f"Connection limit reached, rejecting {peer}")
            writer.close()
            await writer.wait_closed()
            return

        self.active_connections.add(writer)
        logger.info(f"Peer {peer} connected (active: {len(self.active_connections)})")

        try:
            while self.running:
                # Read length prefix with timeout
                try:
                    length_bytes = await asyncio.wait_for(
                        reader.readexactly(self.length_field_size),
                        timeout=30.0,  # 30 second timeout
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout reading from {peer}")
                    break

                payload_len = self.protocol.unpack_length(length_bytes)

                # Validate payload size
                if payload_len > self.max_payload_size:
                    logger.error(f"Payload too large from {peer}: {payload_len} bytes")
                    break

                # Read payload with timeout
                try:
                    payload = await asyncio.wait_for(
                        reader.readexactly(payload_len), timeout=30.0
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout reading payload from {peer}")
                    break

                logger.debug(f"Received {payload_len} bytes from {peer}")

                # Process with ML model
                try:
                    response = self.ml_interface.run_inference(payload)
                    response = self.protocol.pack_message(response)
                    writer.write(response)
                    await writer.drain()
                    logger.debug(f"Sent {len(response)} bytes to {peer}")
                except Exception as e:
                    logger.error(f"ML inference error for {peer}: {e}")
                    # Send error response or break
                    break

        except asyncio.IncompleteReadError:
            logger.info(f"Client {peer} disconnected")
        except Exception as e:
            logger.error(f"Error handling {peer}: {e}")
        finally:
            self.active_connections.discard(writer)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception as e:
                logger.warning(f"Error closing connection for {peer}: {e}")
            logger.info(
                f"Peer {peer} disconnected (active: {len(self.active_connections)})"
            )
