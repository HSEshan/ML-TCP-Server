import asyncio
import logging
from typing import Set

from src.metrics_v2 import Metrics
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
        payload_timeout_seconds: int,
        protocol: Protocol,
        ml_interface: ML_Interface,
        metrics: Metrics,
    ):
        self.host: str = host
        self.port: int = port
        self.protocol: Protocol = protocol
        self.ml_interface: ML_Interface = ml_interface
        self.length_field_size: int = length_field_size
        self.response_size: int = response_size
        self.server: asyncio.Server | None = None
        self.running: bool = True
        self.active_connections: Set[asyncio.StreamWriter] = set()
        self.max_connections: int = max_connections
        self.max_payload_size: int = max_payload_size
        self.payload_timeout_seconds: int = payload_timeout_seconds
        self.metrics = metrics

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

        await self._accept_connection(writer)

        try:
            while self.running:
                payload = await self._read_payload(reader, peer)
                if not payload:
                    continue

                # Process with ML model
                response = await self._process_payload(payload, writer, peer)
                if not response:
                    continue

                await writer.drain()
                self.metrics.add_request()

        except asyncio.IncompleteReadError:
            logger.info("Client %s disconnected", peer)
        except Exception as e:
            logger.error("Error handling %s: %s", peer, e)
            self.metrics.add_error()
        finally:
            await self._cleanup_connection(writer, peer)

    async def _accept_connection(self, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info("peername")

        # Check connection limit
        if len(self.active_connections) >= self.max_connections:
            logger.warning("Connection limit reached, rejecting %s", peer)
            writer.close()
            await writer.wait_closed()
            return

        self.active_connections.add(writer)
        logger.info(
            "Peer %s connected (active: %d)", peer, len(self.active_connections)
        )
        self.metrics.add_connection()

    async def _read_payload(self, reader: asyncio.StreamReader, peer: tuple[str, int]):
        try:
            length_bytes = await asyncio.wait_for(
                reader.readexactly(self.length_field_size),
                timeout=self.payload_timeout_seconds,
            )
        except asyncio.TimeoutError:
            logger.warning("Timeout reading from %s", peer)
            self.metrics.add_error()
            return None

        payload_len = self.protocol.unpack_length(length_bytes)

        if payload_len > self.max_payload_size:
            logger.error("Payload too large from %s: %d bytes", peer, payload_len)
            self.metrics.add_error()
            return None

        try:
            payload = await asyncio.wait_for(
                reader.readexactly(payload_len),
                timeout=self.payload_timeout_seconds,
            )
        except asyncio.TimeoutError:
            logger.warning("Timeout reading payload from %s", peer)
            self.metrics.add_error()
            return None

        logger.debug("Received %d bytes from %s", payload_len, peer)
        return payload

    async def _process_payload(
        self, payload: bytes, writer: asyncio.StreamWriter, peer: tuple[str, int]
    ):
        try:
            response = self.ml_interface.run_inference(payload)
            response = self.protocol.pack_message(response)
            writer.write(response)
            await writer.drain()
            logger.debug("Sent %d bytes to %s", len(response), peer)
        except Exception as e:
            logger.error("ML inference error for %s: %s", peer, e)
            self.metrics.add_inference_error()
            return None
        return response

    async def _cleanup_connection(
        self, writer: asyncio.StreamWriter, peer: tuple[str, int]
    ):
        self.active_connections.discard(writer)
        writer.close()
        try:
            await writer.wait_closed()
            self.metrics.remove_connection()
        except Exception as e:
            logger.warning("Error closing connection for %s: %s", peer, e)
            self.metrics.add_error()
        logger.info(
            "Peer %s disconnected (active: %d)",
            peer,
            len(self.active_connections),
        )
        logger.debug("Active connections: %s", self._get_active_connections())

    def _get_active_connections(self):
        return [w.get_extra_info("peername") for w in self.active_connections]
