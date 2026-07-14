import math

class Vector2:
    def __init__(self, x: float | int, y: float | int = None):
        if y != None:
            self.x, self.y = x, y
        else:
            if isinstance(x, tuple):
                self.x, self.y = x[0], x[1]
            else:
                self.x, self.y = x

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y
    
    def __gt__(self, other) -> bool:
        if isinstance(other, Vector2):
            return self.x > other.x and self.y > other.y
        if isinstance(other, (int, float)):
            return self.magnitude() > other
    
    def __lt__(self, other) -> bool:
        if isinstance(other, Vector2):
            return self.x < other.x and self.y < other.y
        if isinstance(other, (int, float)):
            return self.magnitude() < other

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        if isinstance(other, (int, float)):
            return Vector2(self.x + other, self.y + other)

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        if isinstance(other, (int, float)):
            return Vector2(self.x - other, self.y - other)

    def __mul__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x * other.x, self.y * other.y)
        if isinstance(other, (int, float)):
            return Vector2(self.x * other, self.y * other)

    def __truediv__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x / other.x, self.y / other.y)
        if isinstance(other, (int, float)):
            return Vector2(self.x / other, self.y / other)

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"
    
    def __iter__(self):
        yield self.x
        yield self.y

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0.0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def middle(self, other):
        return Vector2((self.x + other.x) / 2, (self.y + other.y) / 2)

    def distance_to(self, other):
        return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

    def scale(self, factor):
        return Vector2(self.x * factor, self.y * factor)
    
    def copy(self):
        return Vector2(self.x, self.y)
    
    def hash(self):
        return HashVector2(self)


class HashVector2(Vector2):
    def __init__(self, x: float | int | Vector2, y: float | int = None):
        if isinstance(x, Vector2):
            self.x, self.y = x.x, x.y
        else:
            super().__init__(x, y)
    
    def __repr__(self) -> str:
        return f"HashVector2({self.x}, {self.y})"
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __add__(self, other):
        if isinstance(other, HashVector2):
            return HashVector2(self.x + other.x, self.y + other.y)
        return super().__add__(other)

    def __sub__(self, other):
        if isinstance(other, HashVector2):
            return Vector2(self.x - other.x, self.y - other.y)
        return super().__sub__(other)

    def __mul__(self, other):
        if isinstance(other, HashVector2):
            return Vector2(self.x * other.x, self.y * other.y)
        return super().__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, HashVector2):
            return Vector2(self.x / other.x, self.y / other.y)
        return super().__truediv__(other)
    
    def __iter__(self):
        yield self.x
        yield self.y

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0.0:
            return HashVector2(0, 0)
        return HashVector2(self.x / mag, self.y / mag)

    def middle(self, other):
        return HashVector2((self.x + other.x) / 2, (self.y + other.y) / 2)

    def distance_to(self, other):
        return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

    def scale(self, factor):
        return HashVector2(self.x * factor, self.y * factor)
    
    def copy(self):
        return HashVector2(self.x, self.y)
    
    def hash(self):
        return self