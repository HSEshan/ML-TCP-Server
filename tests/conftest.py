import random

from src.ml_interface_abstract import ML_Interface_Abstract

DUMMY_COMMANDS = [b"FD005", b"TR030", b"AS000"]


class MockMLInterface(ML_Interface_Abstract):
    def __init__(self):
        pass

    def run_inference(self, payload: bytes) -> bytes:
        random_command = random.choice(DUMMY_COMMANDS)
        return random_command
