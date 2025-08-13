# Abstract class for ML interface


class ML_Interface:
    def __init__(self):
        pass

    def run_inference(self, payload: bytes) -> bytes:
        return b"a"
