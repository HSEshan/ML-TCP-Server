# Abstract class for ML interface
import os

from src.config import Config


class ML_Interface:
    def __init__(self):
        pass

    def run_inference(self, payload: bytes) -> bytes:
        random_bytes = os.urandom(Config.response_size)
        return random_bytes
