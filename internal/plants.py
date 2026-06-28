from tkinter import Canvas
from internal.vector2 import Vector2
from internal.smartList import SmartList
from internal.sectors import Sectors
from internal.objects import GameObject, PhysicsObject

import random as rand
import config


class Plant(GameObject):
    def __init__(self, sectors: Sectors, objects: SmartList, pos: Vector2, color: tuple[int, int, int],
                plants: SmartList,
                maxRadius: float = rand.uniform(0.5, 2.0),
                growthSpeed: float = rand.uniform(0.1, 0.5),
                rootDepth: float = rand.uniform(0.1, 1.0),
                seedSpeed: float = rand.uniform(0.5, 1.5),
                seedSize: float = rand.uniform(0.1, 0.5)):
        
        super().__init__(sectors, objects, pos, self.maxRadius / 10, color)

        self.plants = plants
        self.plantsIndex = plants.add(self)
        self.rawColor = color
        self.rootDepth = rootDepth
        self.maxRadius = maxRadius
        self.growthSpeed = growthSpeed
        self.seedSpeed = seedSpeed
        self.seedSize = seedSize
        self.health = 100.0
        self.nutrients = 0.0
        self.photoFactor = 0.0
        for i in range(3):
            self.photoFactor += abs(self.rawColor[i] - config.OPTIMAL_PLANT_COLOR[i]) / (255 * 3)
    
    def delete(self, canvas: Canvas):
        super().delete(canvas)
        if self.plantsIndex is not None:
            self.plants.remove(self.plantsIndex)

    def update(self, dt, canvas: Canvas):
        if self.nutrients < 0:
            self.health += self.nutrients
            self.nutrients = 0.0
        
        if self.health <= 0:
            self.delete(canvas)
            return
        
        if self.radius < self.maxRadius:
            self.radius = min(self.maxRadius, self.radius + dt * self.growthSpeed)
            self.nutrients -= dt * self.growthSpeed
        
        

        self.nutrients += dt * self.photoFactor * self.radius
        self.nutrients -= dt * self.radius