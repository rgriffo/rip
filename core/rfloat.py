import struct
from .rserializable import RSerializable

class RFloat(float, RSerializable):

    def __new__(cls, value=0.0, size=4):
        obj = super().__new__(cls, value)
        obj.size = size
        return obj

    def __init__(self, value=0.0):
        self.value = float(value)

    def serialize(self) -> bytearray:
        fmt = self._get_format(self.size)
        return struct.pack(f"{self.byte_order}{fmt}", self)

    @classmethod
    def deserialize(cls, data: bytearray):
        fmt = cls._get_format(cls.size)
        value = struct.unpack(f"{cls.byte_order}{fmt}", data[:cls.size])[0]
        return cls(value)

    def to_dict(self):
        return float(self)

    @classmethod
    def from_dict(cls, data):
        return cls(data)

    @staticmethod
    def _get_format(size):
        return {4: "f", 8: "d"}.get(size, "f")  # Default: float32

    def __repr__(self):
        return f"{self.__class__.__name__}(value={float(self)}, size={self.size})"

    def default(self):
        return float(0)

# Classi derivate con dimensioni fisse
class RFloat32(RFloat):
    size = 4
    def __new__(cls, value=0.0):
        return super().__new__(cls, cls.size)

class RFloat64(RFloat):
    size = 8
    def __new__(cls, value=0.0):
        return super().__new__(cls, cls.size)
