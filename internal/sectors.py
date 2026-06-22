from internal.vector2 import Vector2
from internal.smartList import SmartList

import config


class Sectors:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.sectorSize = Vector2(config.CANVAS_SIZE.x / width, config.CANVAS_SIZE.y / height)
        self.sectors = [[SmartList() for _ in range(width)] for _ in range(height)]
    
    def __repr__(self):
        out = ''''''
        for y in range(self.height):
            out += str(self.sectors[y]) + "\n"
        return out
    
    def get_sector(self, pos: Vector2) -> SmartList:
        if 0 <= pos.x < self.width and 0 <= pos.y < self.height:
            return self.sectors[pos.y][pos.x]
        else:
            raise IndexError("Position out of bounds")
    
    def add_to_sector(self, pos: Vector2, item) -> int:
        return self.get_sector(pos).add(item)
    
    def remove_from_sector(self, pos: Vector2, index: int) -> None:
        sector = self.get_sector(pos)
        sector.remove(index)