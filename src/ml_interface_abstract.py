from abc import ABC, abstractmethod


class ML_Interface_Abstract(ABC):
    @abstractmethod
    def run_inference(self, payload: bytes) -> bytes:
        pass

    @abstractmethod
    async def async_run_inference(self, payload: bytes) -> bytes:
        pass
