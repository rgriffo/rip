from .rserializable import RSerializable

class RString(str, RSerializable):
    def __new__(cls, value="", size=32):
        obj = super().__new__(cls, value[:size])
        obj.size = size
        return obj

    def serialize(self) -> bytearray:
        encoded = self.encode("utf-8")
        return encoded.ljust(self.size, b'\x00')

    @classmethod
    def deserialize(cls, data: bytearray):
        decoded = data[:cls.size].rstrip(b'\x00').decode("utf-8")
        return cls(decoded)

    def to_dict(self) -> str:
        return str(self)

    @classmethod
    def from_dict(cls, data):
        return cls(data)

    def default(self):
        return 'Default'

    def __repr__(self):
        return f"{self.__class__.__name__}(value='{str(self)}', size={self.size})"

# Classi derivate con dimensioni fisse
class RString8(RString):
    size = 8
    def __new__(cls, value=""):
        return super().__new__(cls, value, cls.size)

class RString16(RString):
    size = 16
    def __new__(cls, value=""):
        return super().__new__(cls, value, cls.size)


class RString32(RString):
    size = 32
    def __new__(cls, value=""):
        return super().__new__(cls, value, cls.size)

class RString40(RString):
    size = 40
    def __new__(cls, value=""):
        return super().__new__(cls, value, cls.size)

class RString64(RString):
    size = 64
    def __new__(cls, value=""):
        return super().__new__(cls, value, cls.size)

class RString128(RString):
    size = 128
    def __new__(cls, value=""):
        return super().__new__(cls, value, cls.size)

class RString256(RString):
    size = 256
    def __new__(cls, value=""):
        return super().__new__(cls, value, cls.size)
