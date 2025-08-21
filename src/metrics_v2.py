import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class MetricsEvent:
    event_type: str
    timestamp: float
    data: Optional[dict] = None


class Metrics:
    def __init__(self, batch_size: int = 100, flush_interval: float = 1.0):
        self.metrics = {
            "initial_time": time.time(),
            "uptime": 0,
            "connections": 0,
            "total_requests": 0,
            "requests_per_second": 0,
            "errors": 0,
            "error_rate": 0,
            "inference_errors": 0,
            "inference_error_rate": 0,
            "queue_overload": False,
        }

        # Queue for async processing
        self.event_queue = asyncio.Queue(maxsize=10000)
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        # Consumer task
        self.consumer_task: Optional[asyncio.Task] = None
        self.running = False

    async def start(self):
        """Start the metrics consumer"""
        self.running = True
        self.consumer_task = asyncio.create_task(self._consumer_loop())
        logger.info("Metrics consumer started")

    async def stop(self):
        """Stop the metrics consumer"""
        self.running = False
        if self.consumer_task:
            self.consumer_task.cancel()
            try:
                await self.consumer_task
            except asyncio.CancelledError:
                pass
        logger.info("Metrics consumer stopped")

    def add_request(self):
        try:
            self.event_queue.put_nowait(MetricsEvent("request", time.time()))
        except asyncio.QueueFull:
            self.metrics["queue_overload"] = True

    def add_error(self):
        try:
            self.event_queue.put_nowait(MetricsEvent("error", time.time()))
        except asyncio.QueueFull:
            self.metrics["queue_overload"] = True

    def add_connection(self):
        try:
            self.event_queue.put_nowait(MetricsEvent("connection", time.time()))
        except asyncio.QueueFull:
            self.metrics["queue_overload"] = True

    def remove_connection(self):
        try:
            self.event_queue.put_nowait(MetricsEvent("disconnection", time.time()))
        except asyncio.QueueFull:
            self.metrics["queue_overload"] = True

    def add_inference_error(self):
        try:
            self.event_queue.put_nowait(MetricsEvent("inference_error", time.time()))
        except asyncio.QueueFull:
            self.metrics["queue_overload"] = True

    async def get_metrics(self):
        """Get current metrics"""
        return self.metrics.copy()

    async def _consumer_loop(self):
        """Background consumer that processes metrics events"""
        batch = deque()
        last_flush = time.time()

        while self.running:
            self.metrics["uptime"] = time.time() - self.metrics["initial_time"]
            try:
                try:
                    event = await asyncio.wait_for(
                        self.event_queue.get(), timeout=self.flush_interval
                    )
                    batch.append(event)
                except asyncio.TimeoutError:
                    pass

                # Flush if batch is full or timeout reached
                current_time = time.time()
                if len(batch) >= self.batch_size or (
                    len(batch) > 0 and current_time - last_flush >= self.flush_interval
                ):

                    await self._process_batch(batch)
                    batch.clear()
                    last_flush = current_time

            except asyncio.CancelledError:
                logger.info("Consumer loop cancelled")
                break
            except Exception as e:
                logger.error(f"Metrics consumer error: {e}")
                raise

    async def _process_batch(self, batch: deque):
        """Process a batch of metrics events"""
        for event in batch:
            if event.event_type == "request":
                self.metrics["total_requests"] += 1
            elif event.event_type == "error":
                self.metrics["errors"] += 1
            elif event.event_type == "connection":
                self.metrics["connections"] += 1
            elif event.event_type == "disconnection":
                self.metrics["connections"] -= 1
            elif event.event_type == "inference_error":
                self.metrics["inference_errors"] += 1
        self._update_derived_metrics()

    def _update_derived_metrics(self):
        """Update calculated metrics"""
        current_time = time.time()
        self.metrics["uptime"] = current_time - self.metrics["initial_time"]

        if self.metrics["total_requests"] > 0:
            self.metrics["requests_per_second"] = (
                self.metrics["total_requests"] / self.metrics["uptime"]
            )
            self.metrics["error_rate"] = (
                self.metrics["errors"] / self.metrics["total_requests"]
            )
            self.metrics["inference_error_rate"] = (
                self.metrics["inference_errors"] / self.metrics["total_requests"]
            )


# Create shared instance
metrics = Metrics()
