import struct
from .rserializable import RSerializable

class RInt(int, RSerializable):
    def __new__(cls, value=0, size=4, signed=True):
        obj = super().__new__(cls, value)
        obj.size = size
        obj.signed = signed
        return obj

    def serialize(self) -> bytearray:
        fmt = self._get_format(self.size, self.signed)
        return struct.pack(f"{self.byte_order}{fmt}", self)

    @classmethod
    def deserialize(cls, data: bytearray):
        fmt = cls._get_format(cls.size, cls.signed)
        value = struct.unpack(f"{cls.byte_order}{fmt}", data[:cls.size])[0]
        return cls(value)

    def to_dict(self) -> int:
        return int(self)

    @classmethod
    def from_dict(cls, data):
        return cls(data)

    def default(self):
        return 0

    @staticmethod
    def _get_format(size, signed):
        return {
            (1, True): "b", (1, False): "B",
            (2, True): "h", (2, False): "H",
            (4, True): "i", (4, False): "I",
            (8, True): "q", (8, False): "Q",
        }.get((size, signed), "i")  # Default: int32

    def __repr__(self):
        sign_type = "signed" if self.signed else "unsigned"
        return f"{self.__class__.__name__}(value={int(self)}, size={self.size}, {sign_type})"


class RInt8(RInt):
    size = 1
    signed = True
    def __new__(cls, value=0):
        return super().__new__(cls, value, cls.size, cls.signed)

class RInt16(RInt):
    size = 2
    signed = True
    def __new__(cls, value=0):
        return super().__new__(cls, value, cls.size, cls.signed)

class RInt32(RInt):
    size = 4
    signed = True
    def __new__(cls, value=0):
        return super().__new__(cls, value, cls.size, cls.signed)

class RInt64(RInt):
    size = 8
    signed = True
    def __new__(cls, value=0):
        return super().__new__(cls, value, cls.size, cls.signed)

class RUint8(RInt):
    size = 1
    signed = False
    def __new__(cls, value=0):
        return super().__new__(cls, value, cls.size, cls.signed)

class RUint16(RInt):
    size = 2
    signed = False
    def __new__(cls, value=0):
        return super().__new__(cls, value, cls.size, cls.signed)

class RUint32(RInt):
    size = 4
    signed = False
    def __new__(cls, value=0):
        return super().__new__(cls, value, cls.size, cls.signed)

class RUint64(RInt):
    size = 8
    signed = False
    def __new__(cls, value=0):
        return super().__new__(cls, value, cls.size, cls.signed)

