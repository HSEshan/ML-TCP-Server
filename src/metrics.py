import asyncio
import time


class Metrics:
    def __init__(self):
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
        }
        self.metrics_lock = asyncio.Lock()

    async def get_metrics(self):
        async with self.metrics_lock:
            self.metrics["uptime"] = time.time() - self.metrics["initial_time"]
            if self.metrics["total_requests"] > 0:
                self.metrics["requests_per_second"] = self.metrics["total_requests"] / (
                    time.time() - self.metrics["initial_time"]
                )
                self.metrics["error_rate"] = (
                    self.metrics["errors"] / self.metrics["total_requests"]
                )
                self.metrics["inference_error_rate"] = (
                    self.metrics["inference_errors"] / self.metrics["total_requests"]
                )
            return self.metrics

    async def add_connection(self):
        async with self.metrics_lock:
            self.metrics["connections"] += 1

    async def remove_connection(self):
        async with self.metrics_lock:
            self.metrics["connections"] -= 1

    async def add_request(self):
        async with self.metrics_lock:
            self.metrics["total_requests"] += 1

    async def add_error(self):
        async with self.metrics_lock:
            self.metrics["errors"] += 1

    async def add_inference_error(self):
        async with self.metrics_lock:
            self.metrics["inference_errors"] += 1


metrics = Metrics()  # Shared metrics instance
