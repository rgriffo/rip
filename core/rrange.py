import struct
from .rserializable import RSerializable

# ToDo.  To be done (not needed for my purposes). Per il momento i range li metto in composites

class RRange(RSerializable):

    def __new__(cls, value=0, size=4, type=True):
        obj = super().__new__(cls, value)
        obj.size = size
        obj.type = type
        return obj
