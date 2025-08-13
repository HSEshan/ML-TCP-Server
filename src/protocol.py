import struct


class Protocol:

    @staticmethod
    def pack_message(payload: bytes) -> bytes:
        """Prefix payload with 4-byte big-endian length."""
        return struct.pack(">I", len(payload)) + payload

    @staticmethod
    def unpack_length(length_bytes: bytes) -> int:
        """Unpack 4-byte big-endian length."""
        return struct.unpack(">I", length_bytes)[0]

    @staticmethod
    def pack_prediction(pred: float) -> bytes:
        """Pack a float64 big-endian."""
        return struct.pack(">d", pred)

    @staticmethod
    def unpack_prediction(pred_bytes: bytes) -> float:
        """Unpack a float64 big-endian."""
        return struct.unpack(">d", pred_bytes)[0]
