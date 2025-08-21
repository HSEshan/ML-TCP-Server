from typing import override

from src.ml_interface_abstract import ML_Interface_Abstract


class ML_Interface(ML_Interface_Abstract):
    """Dummy ML interface"""

    @override
    def run_inference(self, payload: bytes) -> bytes:
        return b"XXXXX"

    @override
    async def async_run_inference(self, payload: bytes) -> bytes:
        return b"XXXXX"
