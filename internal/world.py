from internal.vector2 import Vector2, HashVector2
from internal.smartList import SmartList
from internal.genome import Genome
from internal.color import Color
from internal.funcs import clamp, check_point_circle, check_point_rect, grid_border_search

import random as rand
import config, copy, math, functools


class Sector:
    def __init__(self, nutrients: float):
        self.objects = SmartList()
        self.nutrients = nutrients
        self.baseNutrients = nutrients
        self.shape = None
    
    def __repr__(self):
        return f'''Sector:
    Nutrients: {self.nutrients}
    Base Nutrients: {self.baseNutrients}'''
    
    def add(self, item):
        return self.objects.add(item)
    
    def remove(self, index: int):
        return self.objects.remove(index)

neighbors = [
    Vector2(1, 0),
    Vector2(-1, 0),
    Vector2(0, 1),
    Vector2(0, -1)
]

class Sectors:
    def __init__(self):
        self.width = config.CANVAS_SIZE.x // config.SECTOR_SIZE.x
        self.height = config.CANVAS_SIZE.y // config.SECTOR_SIZE.y
        self.sectorSize = config.SECTOR_SIZE
        self.sectorArea = config.SECTOR_SIZE.x * config.SECTOR_SIZE.y
        self.sectors = [[None for _ in range(self.width)] for _ in range(self.height)]

        for _ in range(config.SECTOR_BLUR_LEVEL):
            initTiles = [[rand.random() for _ in range(self.width)] for _ in range(self.height)]
            for y in range(self.height):
                for x in range(self.width):
                    neighborNuts = []
                    for dPos in neighbors:
                        checkPos = Vector2(x, y) + dPos
                        if 0 <= checkPos.x < self.width and 0 <= checkPos.y < self.height:
                            neighborNuts.append(initTiles[checkPos.y][checkPos.x])
                    
                    if len(neighborNuts) > 0:
                        avg = (initTiles[y][x] + sum(neighborNuts) / len(neighborNuts)) / 2
                        self.sectors[y][x] = Sector(avg)

    
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
    
    @functools.cache
    def get_overlap(self, pos: HashVector2, radius: float, precision: int = 6) -> list[tuple[HashVector2, float]]:
        area = radius ** 2 * math.pi
        bounds = (Vector2(pos.x - radius, pos.y - radius), Vector2(pos.x + radius, pos.y + radius))
        sectors = [[Vector2(x, y) for y in range(bounds[0].y // self.sectorSize.y, bounds[1].y // self.sectorSize.y + 1)] for x in range(bounds[0].x // self.sectorSize.x, bounds[1].x // self.sectorSize.x + 1)]

        if len(sectors) == 1:
            return [(sectors[0][0], 1.0)]
        
        dividedGridSizes = [4 ** i for i in range(1, precision + 2)]
        overlapping = []
        for col in sectors:
            for sector in col:
                sectorBounds = (sector * self.sectorSize, (sector + 1) * self.sectorSize)
                sectorCorners = [
                    [HashVector2(sectorBounds[0].x, sectorBounds[0].y), False],
                    [HashVector2(sectorBounds[1].x, sectorBounds[0].y), False],
                    [HashVector2(sectorBounds[0].x, sectorBounds[1].y), False],
                    [HashVector2(sectorBounds[1].x, sectorBounds[1].y), False]
                ]
                sectorCorners = list(map(lambda x: [x[0], check_point_circle(x[0].hash(), pos.hash(), radius)], sectorCorners))

                overlap = grid_border_search(sectorCorners, pos, radius, dividedGridSizes)
                if overlap > 0.0:
                    overlapping.append((sector, (overlap * self.sectorArea) / area))
        
        return overlapping
    
    def draw(self, canvas):
        for y in range(self.height):
            for x in range(self.width):
                sector = self.sectors[y][x]
                if sector.shape is not None:
                    canvas.delete(sector.shape)
                
                rgb = Color(
                    int((1 - sector.nutrients) * 255),
                    int((0.95 - sector.nutrients * 1.25) * 255),
                    int((0.9 - sector.nutrients * 1.45) * 255)
                )

                sector.shape = canvas.create_rectangle(
                    x * self.sectorSize.x, y * self.sectorSize.y,
                    (x + 1) * self.sectorSize.x, (y + 1) * self.sectorSize.y,
                    fill=rgb.to_hex(),
                    outline=""
                )
    
    def update(self, dt):
        prevTiles = copy.deepcopy(self.sectors)
        for y in range(self.height):
            for x in range(self.width):
                neighborNuts = []
                for dPos in neighbors:
                    checkPos = Vector2(x, y) + dPos
                    if 0 <= checkPos.x < self.width and 0 <= checkPos.y < self.height:
                        neighborNuts.append(prevTiles[checkPos.y][checkPos.x].nutrients)
                
                if len(neighborNuts) > 0:
                    sector = self.get(Vector2(x, y))
                    avg = (sector.nutrients + (sum(neighborNuts) / len(neighborNuts) * dt * 0.1)) / (1.0 + dt * 0.1)

                    sector.nutrients = avg
                
                if sector.nutrients < sector.baseNutrients:
                    sector.nutrients += (sector.baseNutrients - sector.nutrients) * dt * config.SECTOR_REGEN_RATE
                elif sector.nutrients > sector.baseNutrients:
                    sector.nutrients += (sector.baseNutrients - sector.nutrients) * dt * config.SECTOR_DECAY_RATE

class World():
    def __init__(self):
        self.objects: SmartList = SmartList()
        self.updateable: SmartList = SmartList()   
        self.sectors: Sectors = Sectors()
        self.species: list = []
    
    def create_species(self, genome: Genome) -> int:
        self.species.append(genome)