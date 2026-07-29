from internal.funcs import *
from internal.profiler import profiler

import internal.globals as globals


class Color:
    @profiler
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b

    @profiler
    def __repr__(self):
        return f"Color(r={self.r}, g={self.g}, b={self.b})"
    
    @profiler
    def __iter__(self):
        return iter((self.r, self.g, self.b))
    
    # Ensure the color values are clamped between 0 and 255
    @profiler
    def __setattr__(self, name, value):
        if name in ['r', 'g', 'b']:
            self.__dict__[name] = clamp(int(value), 0, 255)
    
    @profiler
    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b
    
    @profiler
    def copy(self):
        return Color(self.r, self.g, self.b)

    @profiler
    def to_hex(self) -> str:
        return f"#{''.join(map(lambda x: hex(x)[2:] if x >= 16 else ''.join(['0', hex(x)[2:]]), self))}"

    @profiler
    def hsv(self) -> tuple[float, float, float]:
        return _hsv(self.r / 255, self.g / 255, self.b / 255)

    @profiler
    def hue(self) -> float:
        return self.hsv()[0]

    @profiler
    def sat(self) -> float:
        return self.hsv()[1]

    @profiler
    def val(self) -> float:
        return self.hsv()[2]


@functools.cache
def _hsv(r: float, g: float, b: float) -> tuple[float, float, float]:
    rgb = [r, g, b]

    maxIndex = rgb.index(max(*rgb))
    minIndex = rgb.index(min(*rgb))

    sat = rgb[maxIndex] - rgb[minIndex]
    hue = maxIndex / 3 + (rgb[(maxIndex + 1) % 3] - rgb[(maxIndex - 1) % 3]) / sat

    return (hue, sat, rgb[maxIndex])