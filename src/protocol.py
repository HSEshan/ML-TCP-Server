import struct

from src.config import Config


class Protocol:

    _size_formats = {
        2: "H",  # 2-byte unsigned short
        4: "I",  # 4-byte unsigned int
        8: "Q",  # 8-byte unsigned long long
    }

    @classmethod
    def pack_message(cls, payload: bytes) -> bytes:
        """Prefix payload with big-endian length."""
        if not isinstance(payload, (bytes, bytearray)):
            raise TypeError("Payload must be bytes")

        fmt_char = cls._size_formats.get(Config.length_field_size)
        if not fmt_char:
            raise ValueError(
                f"Unsupported length field size: {Config.length_field_size}"
            )

        return struct.pack(f">{fmt_char}", len(payload)) + payload

    @classmethod
    def unpack_length(cls, length_bytes: bytes) -> int:
        """Unpack big-endian length."""
        if len(length_bytes) != Config.length_field_size:
            raise ValueError(
                f"Length prefix must be exactly {Config.length_field_size} bytes"
            )

        fmt_char = cls._size_formats.get(Config.length_field_size)
        if not fmt_char:
            raise ValueError(
                f"Unsupported length field size: {Config.length_field_size}"
            )

        try:
            return struct.unpack(f">{fmt_char}", length_bytes)[0]
        except struct.error:
            raise ValueError(f"Invalid length prefix: {length_bytes.hex()}")
