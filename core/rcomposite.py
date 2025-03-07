from .rserializable import RSerializable
from .rlist import RList

class RComposite(RSerializable):
    def __new__(cls):
        obj = super().__new__(cls)
        return obj

    def __init__(self, **kwargs):
        for field, field_type in self.__annotations__.items():
            field_value = kwargs.get(field, None)

            if isinstance(field_value, field_type):
                setattr(self, field, field_value)
            elif field_value is not None:
                setattr(self, field, field_type(field_value))
            else:
                setattr(self, field, field_type())  # Crea un'istanza di default

    def serialize(self) -> bytearray:
        data = bytearray()
        for field in self.__annotations__:
            value = getattr(self, field)
            data.extend(value.serialize())
        return data

    @classmethod
    def deserialize(cls, data: bytearray):
        obj = cls()
        offset = 0
        for field, field_type in cls.__annotations__.items():
            if issubclass(field_type, RList):
                value = field_type.deserialize(data[offset:], obj)
            else:
                value = field_type.deserialize(data[offset:])
            setattr(obj, field, value)
            offset += len(value.serialize())
        return obj

    def to_dict(self) -> dict:
        return {field: getattr(self, field).to_dict() for field in self.__annotations__}

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        for field, field_type in cls.__annotations__.items():
            setattr(obj, field, field_type.from_dict(data[field]))
        return obj

    def size_in_bytes(self) -> int:
        return sum(len(getattr(self, field).serialize()) for field in self.__annotations__)

    def default(self):
        res = {field: getattr(self, field).default() for field in self.__annotations__}
        for field in self.__annotations__:
            if issubclass(getattr(self, field).__class__, RList):
                if not isinstance(getattr(self, field).length_field, int):
                    res[getattr(self, field).length_field] = 1
                else:
                    res[field] = [getattr(self, field).default()[0] for _ in range(getattr(self, field).length_field)]
        return res

    def __repr__(self):
        return f"RComposite(size={self.size_in_bytes()} bytes, byte_order='{self.byte_order}')"
