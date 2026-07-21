from internal.profiler import profiler

import internal.globals as globals
import math, functools

class Vector2:
    @profiler
    def __init__(self, x: float | int, y: float | int = None):
        if y != None:
            self.x, self.y = x, y
        else:
            self.x, self.y = x, x

    @profiler
    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y
    
    @profiler
    def __gt__(self, other) -> bool:
        if isinstance(other, Vector2):
            return self.x > other.x and self.y > other.y
        if isinstance(other, (int, float)):
            return self.magnitude() > other
    
    @profiler
    def __lt__(self, other) -> bool:
        if isinstance(other, Vector2):
            return self.x < other.x and self.y < other.y
        if isinstance(other, (int, float)):
            return self.magnitude() < other

    @profiler
    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        if isinstance(other, (int, float)):
            return Vector2(self.x + other, self.y + other)

    @profiler
    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        if isinstance(other, (int, float)):
            return Vector2(self.x - other, self.y - other)

    @profiler
    def __mul__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x * other.x, self.y * other.y)
        if isinstance(other, (int, float)):
            return Vector2(self.x * other, self.y * other)

    @profiler
    def __truediv__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x / other.x, self.y / other.y)
        if isinstance(other, (int, float)):
            return Vector2(self.x / other, self.y / other)

    @profiler
    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"
    
    @profiler
    def __iter__(self):
        yield self.x
        yield self.y

    @profiler
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    @profiler
    def normalize(self):
        mag = self.magnitude()
        if mag == 0.0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    @profiler
    def middle(self, other):
        out = _middle(self.x, self.y, other.x, other.y)
        return Vector2(out[0], out[1])

    @profiler
    def distance_to(self, other):
        return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

    @profiler
    def scale(self, factor):
        return Vector2(self.x * factor, self.y * factor)
    
    @profiler
    def copy(self):
        return Vector2(self.x, self.y)
    
    @profiler
    def tuple(self):
        return (self.x, self.y)

@functools.cache
def _middle(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float]:
    return ((x1 + x2) / 2, (y1 + y2) / 2)