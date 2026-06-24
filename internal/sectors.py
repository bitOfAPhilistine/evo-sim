from internal.vector2 import Vector2
from internal.smartList import SmartList

import config


class Sectors:
    def __init__(self):
        self.width = config.CANVAS_SIZE.x // config.SECTOR_SIZE.x
        self.height = config.CANVAS_SIZE.y // config.SECTOR_SIZE.y
        self.sectorSize = config.SECTOR_SIZE
        self.sectors = [[SmartList() for _ in range(self.width)] for _ in range(self.height)]
    
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
    
    # Get the given sector and the 8 surrounding sectors
    def get_sectors_around(self, pos: Vector2) -> list[SmartList]:
        sectors = []
        for y in range(max(0, pos.y - 1), min(self.height, pos.y + 2)):
            for x in range(max(0, pos.x - 1), min(self.width, pos.x + 2)):
                sectors.append(self.get_sector(Vector2(x, y)))
        return sectors