import struct
from .rserializable import RSerializable

class RList(RSerializable):
    length_field = None
    element_type = None

    def __new__(cls, element_type=None, length_field=None):
        obj = super().__new__(cls)
        # obj.element_type = element_type
        # obj.length_field = length_field
        return obj

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    def __init__(self, items=None):
        self.items = items if items is not None else []


    def serialize(self) -> bytearray:
        data = bytearray()
        for item in self.items:
            data.extend(item.serialize())
        return data

    @classmethod
    def deserialize(cls, data: bytearray, obj_ref):
        obj = cls()
        offset = 0

        items = []
        _len =  cls.length_field if isinstance(cls.length_field, int) else getattr(obj_ref, cls.length_field)
        for _ in range(_len):
            item = cls.element_type.deserialize(data[offset:])
            items.append(item)
            offset += len(item.serialize())
        setattr(obj, 'items', items)
        return obj

    def to_dict(self) -> list:
        return [item.to_dict() for item in self.items]

    @classmethod
    def from_dict(cls, items):
        items = [cls.element_type.from_dict(item) for item in items]
        return cls(items)

    def default(self):
        return [self.element_type().default()]

    def __repr__(self):
        return f"BaseList(length={len(self.items)}, element_type={self.element_type.__name__})"
