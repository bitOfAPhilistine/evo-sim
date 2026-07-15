from internal.vector2 import Vector2, HashVector2
from internal.smartList import SmartList
from internal.genome import Genome
from internal.color import Color
from internal.funcs import clamp, check_point_circle, check_rect_circle, grid_border_search

import random as rand
import config, copy, math, functools, time


neighbors = [
    Vector2(1, 0),
    Vector2(-1, 0),
    Vector2(0, 1),
    Vector2(0, -1)
]

class Sector:
    def __init__(self, sectorPos: Vector2, size: Vector2, nutrients: float):
        self.objects = SmartList()
        self.sectorPos = sectorPos
        self.bounds = (
            sectorPos * size,
            (sectorPos + 1) * size
        )
        self.nutrients = nutrients
        self.baseNutrients = nutrients
        self.shape = None
    
    def __repr__(self):
        return f'''Sector:
    Position: {self.sectorPos.x:.0f}, {self.sectorPos.y:.0f}
    Nutrients: {self.nutrients:.4f}
    Base Nutrients: {self.baseNutrients:.4f}'''
    
    def add(self, item):
        return self.objects.add(item)
    
    def remove(self, index: int):
        return self.objects.remove(index)

    def get_overlap(self, pos: Vector2, radius: float, precision: int) -> float:
        sectorCorners = [
            [HashVector2(self.bounds[0].x, self.bounds[0].y), False],
            [HashVector2(self.bounds[1].x, self.bounds[0].y), False],
            [HashVector2(self.bounds[0].x, self.bounds[1].y), False],
            [HashVector2(self.bounds[1].x, self.bounds[1].y), False]
        ]
        sectorCorners = tuple(map(lambda x: (x[0], check_point_circle(x[0], pos.hash(), radius)), sectorCorners))

        return grid_border_search(sectorCorners, pos.hash(), tuple([4 ** i for i in range(precision + 1)]))

class Sectors:
    def __init__(self):
        self.width = config.CANVAS_SIZE.x // config.SECTOR_SIZE.x
        self.height = config.CANVAS_SIZE.y // config.SECTOR_SIZE.y
        self.sectorSize = config.SECTOR_SIZE
        self.sectorArea = config.SECTOR_SIZE.x * config.SECTOR_SIZE.y
        self.sectors: list[list[Sector | None]] = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.lastUpdated = 0.0

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
                        self.sectors[y][x] = Sector(Vector2(x, y), config.SECTOR_SIZE, avg)

    
    def get(self, pos: Vector2) -> Sector | None:
        if 0 <= pos.x < self.width and 0 <= pos.y < self.height:
            return self.sectors[pos.y][pos.x]
        else:
            return None
    
    def get_overlapping(self, pos: Vector2, radius: float) -> list[Sector]:
        bounds = (Vector2(pos.x - radius, pos.y - radius), Vector2(pos.x + radius, pos.y + radius))
        sectors = [[Vector2(x, y) for y in range(
            max(0, int(bounds[0].y) // self.sectorSize.y),
            min(self.height, (int(bounds[1].y) // self.sectorSize.y) + 1)
        )] for x in range(
            max(0, int(bounds[0].x) // self.sectorSize.x),
            min(self.width, (int(bounds[1].x) // self.sectorSize.x) + 1)
        )]

        if len(sectors) == 1:
            return [self.get(sectors[0][0])]
        
        output = []
        for col in sectors:
            for sector in col:
                if check_rect_circle(self.get(sector).bounds[0].hash(), self.get(sector).bounds[1].hash(), pos.hash(), radius):
                    output.append(self.get(sector))
        return output
    
    def add_to_sectors(self, object, sectors: list[Sector]) -> list[int]:
        output = []
        for sector in sectors:
            output.append(sector.add(object))
        return output
    
    def remove_from_sectors (self, sectors: list[Sector, int], indices: list[int]):
        for sector, index in zip(sectors, indices, strict=True):
            sector.remove(index)
    
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
    
    def update(self):
        dt = time.time() - self.lastUpdated
        prevTiles = copy.deepcopy(self.sectors)
        for y in range(self.height):
            for x in range(self.width):
                sector = self.get(Vector2(x, y))

                neighborNuts = []
                for dPos in neighbors:
                    checkPos = Vector2(x, y) + dPos
                    if 0 <= checkPos.x < self.width and 0 <= checkPos.y < self.height:
                        neighborNuts.append(prevTiles[checkPos.y][checkPos.x].nutrients)
                
                if len(neighborNuts) > 0:
                    avg = (sector.nutrients + (sum(neighborNuts) / len(neighborNuts) * dt * 0.1)) / (1.0 + dt * 0.1)

                    sector.nutrients = avg
                
                if sector.nutrients < sector.baseNutrients:
                    sector.nutrients += (sector.baseNutrients - sector.nutrients) * dt * config.SECTOR_REGEN_RATE
                elif sector.nutrients > sector.baseNutrients:
                    sector.nutrients += (sector.baseNutrients - sector.nutrients) * dt * config.SECTOR_DECAY_RATE
        self.lastUpdated = time.time()

class World():
    def __init__(self):
        self.objects: SmartList = SmartList()
        self.updateable: SmartList = SmartList()   
        self.sectors: Sectors = Sectors()
        self.species: list = []
        self.plantCount: int = 0
        self.seedCount: int = 0
        self.overlapRequests: list = []
    
    def request_overlaps(self, object):
        self.overlapRequests.append(object)
    
    def create_species(self, genome: Genome) -> int:
        self.species.append(genome)
    
    def update(self, canvas, dt, startTime):
        frameTime = 0.0
        for obj in self.updateable:
            if obj:
                try:
                    obj.update(dt, canvas)
                except OverflowError:
                    obj.delete(canvas)
        
        while frameTime < config.TARGET_FRAMERATE and len(self.overlapRequests) > 0:
            obj = self.overlapRequests.pop(0)
            overlaps = [0.0 for _ in obj.sectors]

            for i in range(len(obj.sectors)):
                overlaps[i] = obj.sectors[i].get_overlap(obj.pos, obj.radius, config.areaCalcPrecision) * self.sectors.sectorArea / obj.area
            
            obj.sectorOverlaps = overlaps
            obj.queued = False
            frameTime = time.time() - startTime
        
        if frameTime < config.TARGET_FRAMERATE or time.time() - self.sectors.lastUpdated > config.maxTimeBetweenSectorSmoothing:
            self.sectors.update()