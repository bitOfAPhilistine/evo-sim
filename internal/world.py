from internal.vector2 import Vector2
from internal.smartList import SmartList
from internal.genome import Genome
from internal.color import Color
from internal.funcs import *
from internal.profiler import profiler

import internal.globals as globals
import random as rand
import config, copy, math, functools, time


neighbors = [
    Vector2(1, 0),
    Vector2(-1, 0),
    Vector2(0, 1),
    Vector2(0, -1)
]

class Sector:
    @profiler
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
        self.rgb = Color(0, 0, 0)
    
    @profiler
    def readout(self):
        return f'''Sector:
    Position: {self.sectorPos.x:.0f}, {self.sectorPos.y:.0f}
    Nutrients: {self.nutrients:.4f}
    Base Nutrients: {self.baseNutrients:.4f}'''
    
    @profiler
    def add(self, item):
        return self.objects.add(item)
    
    @profiler
    def remove(self, index: int):
        return self.objects.remove(index)

    @profiler
    @functools.cache
    def get_overlap(self, posx: float, posy: float, radius: float, precision: int) -> float:
        pos = Vector2(posx, posy)
        sectorCorners = [
            [Vector2(self.bounds[0].x, self.bounds[0].y), False],
            [Vector2(self.bounds[1].x, self.bounds[0].y), False],
            [Vector2(self.bounds[0].x, self.bounds[1].y), False],
            [Vector2(self.bounds[1].x, self.bounds[1].y), False]
        ]
        sectorCorners = tuple(map(lambda x: (x[0], check_point_circle(x[0], pos, radius)), sectorCorners))

        return grid_border_search(sectorCorners, pos, radius, divided_grid_sizes(precision))
    
    @profiler
    def draw(self, canvas, isMonitored):
        rgb = Color(
            int((1 - self.nutrients) * 255),
            int((0.95 - self.nutrients * 1.25) * 255),
            int((0.9 - self.nutrients * 1.45) * 255)
        )

        if self.rgb != rgb or isMonitored:
            if self.shape is not None:
                canvas.delete(self.shape)

            self.shape = canvas.create_rectangle(
                self.bounds[0].x, self.bounds[0].y,
                self.bounds[1].x, self.bounds[1].y,
                fill=rgb.to_hex(),
                outline="blue" if isMonitored else ""
            )
            self.rgb = rgb

class Sectors:
    @profiler
    def __init__(self):
        self.width = config.CANVAS_SIZE.x // config.SECTOR_SIZE.x
        self.height = config.CANVAS_SIZE.y // config.SECTOR_SIZE.y
        self.sectorSize = config.SECTOR_SIZE
        self.sectorArea = config.SECTOR_SIZE.x * config.SECTOR_SIZE.y
        self.sectors: list[list[Sector | None]] = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.lastUpdated = time.time()

        for _ in range(config.SECTOR_BLUR_LEVEL):
            initTiles = [[rand.uniform(0.0, 1.0) for _ in range(self.width)] for _ in range(self.height)]
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

    @profiler
    def get(self, pos: Vector2) -> Sector | None:
        if 0 <= pos.x < self.width and 0 <= pos.y < self.height:
            return self.sectors[pos.y][pos.x]
        else:
            return None
    
    @profiler
    def get_overlapping(self, pos: Vector2, radius: float) -> list[Sector]:
        bounds = (Vector2(pos.x - radius, pos.y - radius), Vector2(pos.x + radius, pos.y + radius))
        sectors = [[Vector2(x, y) for y in range(
            max(0, int(bounds[0].y // self.sectorSize.y)),
            min(self.height, int(bounds[1].y // self.sectorSize.y) + 1)
        )] for x in range(
            max(0, int(bounds[0].x // self.sectorSize.x)),
            min(self.width, int(bounds[1].x // self.sectorSize.x) + 1)
        )]

        if len(sectors) == 1 and len(sectors[0]) == 1:
            return [self.get(sectors[0][0])]
        
        output = []
        for col in sectors:
            for sector in col:
                if check_rect_circle(self.get(sector).bounds[0], self.get(sector).bounds[1], pos, radius):
                    output.append(self.get(sector))
        return output
    
    @profiler
    def add_to_sectors(self, object, sectors: list[Sector]) -> list[int]:
        output = []
        for sector in sectors:
            output.append(sector.add(object))
        return output
    
    @profiler
    def remove_from_sectors (self, sectors: list[Sector], indices: list[int]):
        for sector, index in zip(sectors, indices, strict=True):
            sector.remove(index)
    
    @profiler
    def draw(self, canvas):
        for y in range(self.height):
            for x in range(self.width):
                sector = self.sectors[y][x]
                if globals.monitoring != sector:
                    sector.draw(canvas, False)
        
        if isinstance(globals.monitoring, Sector):
            globals.monitoring.draw(canvas, True)
    
    @profiler
    def update(self):
        dt = min(config.TARGET_FRAMERATE * 10.0, time.time() - self.lastUpdated)
        prevTiles = [[self.get(Vector2(x, y)).nutrients for y in range(self.height)] for x in range(self.width)]

        for y in range(self.height):
            for x in range(self.width):
                sector = self.get(Vector2(x, y))

                neighborNuts = []
                for dPos in neighbors:
                    checkPos = Vector2(x, y) + dPos
                    if 0 <= checkPos.x < self.width and 0 <= checkPos.y < self.height:
                        neighborNuts.append(prevTiles[checkPos.x][checkPos.y])
                
                if len(neighborNuts) > 0:
                    avg = (sector.nutrients + (sum(neighborNuts) / len(neighborNuts) * dt * 0.1)) / (1.0 + dt * 0.1)

                    sector.nutrients = avg
                
                if sector.nutrients < sector.baseNutrients:
                    sector.nutrients += (sector.baseNutrients - sector.nutrients) * dt * config.SECTOR_REGEN_RATE
                elif sector.nutrients > sector.baseNutrients:
                    sector.nutrients += (sector.baseNutrients - sector.nutrients) * dt * config.SECTOR_DECAY_RATE
        self.lastUpdated = time.time()

class World():
    @profiler
    def __init__(self):
        self.objects: SmartList = SmartList()
        self.updateable: SmartList = SmartList() 
        self.updateable0Index: int = 0  
        self.sectors: Sectors = Sectors()
        self.species: list = []
        self.plantCount: int = 0
        self.seedCount: int = 0
        self.overlapRequests: list = []
    
    @profiler
    def request_overlaps(self, obj):
        self.overlapRequests.append(obj)
        obj.queued = True
    
    @profiler
    def create_species(self, genome: Genome) -> int:
        self.species.append(genome)
    
    @profiler
    def update(self, canvas, dt, startTime):
        frameTime = 0.0
        
        while frameTime < config.TARGET_FRAMERATE and len(self.overlapRequests) > 0:
            obj = self.overlapRequests.pop(0)
            overlaps = [0.0 for _ in obj.sectors]

            for i in range(len(obj.sectors)):
                overlaps[i] = obj.sectors[i].get_overlap(obj.pos.x, obj.pos.y, obj.radius, config.areaCalcPrecision) * self.sectors.sectorArea / obj.area
            
            obj.sectorOverlaps = overlaps
            obj.queued = False
            frameTime = time.time() - startTime
        
        if len(self.updateable) > 0:
            for i in [(self.updateable0Index + i) % len(self.updateable) for i in range(len(self.updateable))]:
                if frameTime < config.TARGET_FRAMERATE * 2.0:
                    obj = self.updateable[i]
                    if obj:
                        try:
                            obj.update(canvas)
                        except OverflowError:
                            obj.delete(canvas)
                    
                    frameTime = time.time() - startTime
                else:
                    self.updateable0Index = (i + 1) % len(self.updateable)
                    break
        
        if frameTime < config.TARGET_FRAMERATE or time.time() - self.sectors.lastUpdated > config.maxTimeBetweenSectorSmoothing:
            self.sectors.update()
        
        frameTime = time.time() - startTime
        if frameTime > config.TARGET_FRAMERATE * 5:
            config.areaCalcPrecision = max(config.MIN_AREA_CALC_PRECISION, config.areaCalcPrecision - 1)
        elif frameTime < config.TARGET_FRAMERATE:
            config.areaCalcPrecision = min(config.MAX_AREA_CALC_PRECISION, config.areaCalcPrecision + 1)