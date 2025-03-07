import struct
from .rserializable import RSerializable

class RUnion(RSerializable):
    possible_types = {}

    def __new__(cls, possible_types=None, tag_field_size=1):
        obj = super().__new__(cls)
        if not obj.possible_types:
            obj.possible_types = possible_types or {}
        obj.tag_field_size = tag_field_size
        obj.selected_type = None
        obj.value = None
        return obj

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "possible_types") or not cls.possible_types:
            raise ValueError(f"La classe {cls.__name__} deve avere un attributo 'possible_types'.")

    def __init__(self, selected_type=None, value=None):
        if selected_type and selected_type in self.possible_types:
            self.selected_type = selected_type
            self.value = self.possible_types[selected_type](value)
        else:
            self.selected_type = list(self.possible_types.keys())[0]
            self.value = self.possible_types[self.selected_type]()

    def serialize(self) -> bytearray:
        data = bytearray()
        type_index = list(self.possible_types.keys()).index(self.selected_type)
        data.extend(struct.pack(f"{self.byte_order}{self._get_format(self.tag_field_size)}", type_index))
        data.extend(self.value.serialize())
        return data

    @classmethod
    def deserialize(cls, data: bytearray):
        obj = cls()
        offset = 0
        type_index = struct.unpack(f"{cls.byte_order}{cls._get_format(obj.tag_field_size)}", data[:obj.tag_field_size])[0]
        offset += obj.tag_field_size

        selected_type = list(cls.possible_types.keys())[type_index]
        value = cls.possible_types[selected_type]().deserialize(data[offset:])

        return cls(selected_type, value)

    def to_dict(self) -> dict:
        return {self.selected_type: self.value.to_dict()}

    @classmethod
    def from_dict(cls, data):
        selected_type = list(data.keys())[0]
        value = data[selected_type]
        return cls(selected_type, value)

    def __repr__(self):
        return f"BaseUnion(selected_type={self.selected_type}, value={self.value}, tag_field_size={self.tag_field_size})"
