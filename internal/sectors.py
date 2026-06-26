from internal.vector2 import Vector2
from internal.smartList import SmartList

import random as rand
import config
import copy


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


class Sector:
    def __init__(self, nutrients: float):
        self.objects = SmartList()
        self.nutrients = nutrients
        self.shape = None
    
    def add(self, item):
        return self.objects.add(item)
    
    def remove(self, index: int):
        return self.objects.remove(index)

class Sectors:
    def __init__(self, blurLevel: int):
        self.width = config.CANVAS_SIZE.x // config.SECTOR_SIZE.x
        self.height = config.CANVAS_SIZE.y // config.SECTOR_SIZE.y
        self.sectorSize = config.SECTOR_SIZE
        self.sectors = [[Sector(rand.random()) for _ in range(self.width)] for _ in range(self.height)]

        for _ in range(blurLevel):
            prevTiles = copy.deepcopy(self.sectors)
            for y in range(self.height):
                for x in range(self.width):
                    neighbors = []
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                neighbors.append(prevTiles[ny][nx].nutrients)
                    if neighbors:
                        self.sectors[y][x] = Sector(sum(neighbors) / len(neighbors))
    
    def get(self, pos: Vector2) -> Sector:
        if 0 <= pos.x < self.width and 0 <= pos.y < self.height:
            return self.sectors[pos.y][pos.x]
        else:
            raise IndexError("Position out of bounds")
    
    # Get the given sector and the 8 surrounding sectors
    def get_sectors_around(self, pos: Vector2) -> list[Sector]:
        sectors = []
        for y in range(max(0, pos.y - 1), min(self.height, pos.y + 2)):
            for x in range(max(0, pos.x - 1), min(self.width, pos.x + 2)):
                sectors.append(self.get(Vector2(x, y)))
        return sectors
    
    def draw(self, canvas):
        for y in range(self.height):
            for x in range(self.width):
                sector = self.sectors[y][x]
                if sector.shape is not None:
                    canvas.delete(sector.shape)
                
                rgb = (
                    clamp(int((1 - sector.nutrients) * 255 * 2.5), 0, 255),
                    clamp(int((1 - sector.nutrients) * 255 * 1.5), 0, 255),
                    clamp(int((0.9 - sector.nutrients) * 255), 0, 255)
                )

                sector.shape = canvas.create_rectangle(
                    x * self.sectorSize.x, y * self.sectorSize.y,
                    (x + 1) * self.sectorSize.x, (y + 1) * self.sectorSize.y,
                    fill=f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
                    outline=""
                )