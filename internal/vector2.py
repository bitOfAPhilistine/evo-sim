from internal.profiler import profiler

import internal.globals as globals
import math

class Vector2:
    @profiler
    def __init__(self, x: float | int, y: float | int = None):
        if y != None:
            self.x, self.y = x, y
        else:
            if isinstance(x, tuple):
                self.x, self.y = x[0], x[1]
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
        return Vector2((self.x + other.x) / 2, (self.y + other.y) / 2)

    @profiler
    def distance_to(self, other):
        return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

    @profiler
    def scale(self, factor):
        return Vector2(self.x * factor, self.y * factor)
    
    @profiler
    def copy(self):
        return Vector2(self.x, self.y)