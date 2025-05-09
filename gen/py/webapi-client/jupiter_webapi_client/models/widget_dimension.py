from enum import Enum


class WidgetDimension(str, Enum):
    KX1 = "kx1"
    KX2 = "kx2"
    KX3 = "kx3"
    VALUE_0 = "1x1"
    VALUE_1 = "1x2"
    VALUE_2 = "1x3"
    VALUE_3 = "2x1"
    VALUE_4 = "2x2"
    VALUE_5 = "2x3"
    VALUE_6 = "3x1"
    VALUE_7 = "3x2"
    VALUE_8 = "3x3"

    def __str__(self) -> str:
        return str(self.value)
