from internal.clamp import clamp


class Color:
    def __init__(self, r: int, g: int, b: int):
        self.r = clamp(r, 0, 255)
        self.g = clamp(g, 0, 255)
        self.b = clamp(b, 0, 255)

    def __repr__(self):
        return f"Color(r={self.r}, g={self.g}, b={self.b})"
    
    def __iter__(self):
        return iter((self.r, self.g, self.b))
    
    def to_hex(self) -> str:
        return f"#{''.join(map(lambda x: hex(x)[2:] if x >= 16 else ''.join(['0', hex(x)[2:]]), self))}"