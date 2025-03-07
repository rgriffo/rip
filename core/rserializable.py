from collections import OrderedDict

class RSerializable:
    byte_order = "<"
    list_length_field_size = 4
    enum_size = 4

    @classmethod
    def __prepare__(metacls, name, bases):
        return OrderedDict()

    @classmethod
    def set_byte_order(cls, order: str):
        if order not in ["<", ">"]:
            raise ValueError("Byte order must be '<' (little-endian) or '>' (big-endian)")
        cls.byte_order = order

    @classmethod
    def set_list_length_field_size(cls, size: int):
        if size not in [1, 2, 4, 8]:
            raise ValueError("Possible length available in bytes: [1, 2, 4, 8].")
        cls.list_length_field_size = size

    @staticmethod
    def _get_format(size):
        return {1: "B", 2: "H", 4: "I", 8: "Q"}.get(size, "I")
