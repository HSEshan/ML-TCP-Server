from src.ml_interface_abstract import ML_Interface_Abstract


class ML_Interface(ML_Interface_Abstract):
    """Dummy ML interface"""

    def run_inference(self, payload: bytes) -> bytes:
        return b"XXXXX"
