import logging

from aiohttp import web

from src.config import config, debug_config
from src.metrics import Metrics
from src.ml_interface import ML_Interface
from src.protocol import Protocol
from src.tcp_server import TCP_Server


def setup_tcp_server(metrics: Metrics) -> TCP_Server:
    logger = logging.getLogger(__name__)

    server = TCP_Server(
        host=config.host,
        port=config.port,
        length_field_size=config.length_field_size,
        response_size=config.response_size,
        max_connections=config.max_connections,
        max_payload_size=config.max_payload_size_kb * 1024,
        payload_timeout_seconds=config.payload_timeout_seconds,
        protocol=Protocol(),
        ml_interface=ML_Interface(),
        metrics=metrics,
    )

    logger.debug("Config: %s", debug_config())

    return server


async def http_handler(request):
    metrics: Metrics = request.app["metrics"]
    data = await metrics.get_metrics()
    print(data)
    return web.json_response(data)


async def setup_http_server(metrics: Metrics, port: int = 8080) -> web.TCPSite:
    app = web.Application()
    app["metrics"] = metrics
    app.router.add_get("/metrics", http_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    return site
