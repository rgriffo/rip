import struct
from .rserializable import RSerializable

class RBool(int, RSerializable):
    def __new__(cls, value=False):
        obj = int.__new__(cls, 1 if value else 0)
        return obj

    def serialize(self):
        return struct.pack("?", bool(self))

    @classmethod
    def deserialize(cls, data: bytearray):
        value = struct.unpack("?", data[:1])[0]
        return cls(value)

    def to_dict(self) -> bool:
        return bool(self)

    @classmethod
    def from_dict(cls, data):
        return cls(bool(data))

    def default(self):
        return False