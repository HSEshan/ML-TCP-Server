import asyncio
import logging

from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse

from src.metrics_v2 import metrics

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/metrics")
async def get_metrics():
    data = await metrics.get_metrics()
    return JSONResponse(content=data)


@app.websocket("/metrics")
async def ws_metrics(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await metrics.get_metrics()
            await websocket.send_json(data)
            await asyncio.sleep(0.25)
    except Exception as e:
        logger.error(f"Error in websocket metrics: {e}")
        await websocket.close()
