import struct
from .rserializable import RSerializable

class REnum(int, RSerializable):
    size_in_bytes = 1
    values: dict = {}
    symbols: dict = {}

    def __new__(cls, value=None):
        if not cls.values:
            raise ValueError(f"Enum {cls.__name__} non ha valori definiti.")
        if value is None:
            value = list(cls.values.values())[0]
        if value not in cls.values.values():
            raise ValueError(f"Valore {value} non valido per {cls.__name__}")
        obj = super().__new__(cls, value)
        return obj

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "values") or not cls.values:
            raise ValueError(f"La classe {cls.__name__} deve avere un attributo 'values'.")
        cls.symbols = {v: k for k, v in cls.values.items()}

    @classmethod
    def from_value(cls, value: int):
        if value in cls.symbols:
            return cls(value)
        raise ValueError(f"Valore {value} non valido per {cls.__name__}")

    @classmethod
    def from_string(cls, name: str):
        if name in cls.values:
            return cls(cls.values[name])
        raise ValueError(f"Nome {name} non valido per {cls.__name__}")

    def serialize(self):
        return struct.pack(f"{self.byte_order}{self._get_format(self.size_in_bytes)}", int(self))

    @classmethod
    def deserialize(cls, data: bytearray):
        value = struct.unpack(f"{cls.byte_order}{cls._get_format(cls.size_in_bytes)}", data[:cls.size_in_bytes])[0]
        return cls.from_value(value)

    def to_dict(self):
        return self.symbols.get(self, int(self))

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, int):
            return cls.from_value(data)
        elif isinstance(data, str):
            return cls.from_string(data)
        raise ValueError(f"Invalid format for {cls.__name__}: {data}")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_dict()}, size={self.size_in_bytes}, byte_order='{self.byte_order}')"

    def default(self):
        return self.symbols[list(self.values.values())[0]]