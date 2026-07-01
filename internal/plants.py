from tkinter import Canvas
from internal.vector2 import Vector2
from internal.smartList import SmartList
from internal.sectors import Sectors, clamp
from internal.objects import GameObject, PhysicsObject

import random as rand
import config


class Plant(GameObject):
    def __init__(self, sectors: Sectors, objects: SmartList, plants: SmartList, pos: Vector2,
                maxRadius: float = rand.uniform(5.0, 10.0),
                growthSpeed: float = rand.uniform(0.1, 0.5),
                rootDepth: float = rand.uniform(0.1, 1.0),
                seedSpeed: float = rand.uniform(0.5, 1.5),
                seedSize: float = rand.uniform(0.1, 0.5)):
        
        super().__init__(sectors, objects, pos, maxRadius / 5, config.HEALTHY_PLANT_COLOR)

        self.plants = plants
        self.plantsIndex = plants.add(self)
        self.rootDepth = clamp(rootDepth, 0.0, 1.0)
        self.maxRadius = clamp(maxRadius, 1.0, 50.0)
        self.growthSpeed = clamp(growthSpeed, 0.0, 2.0)
        self.seedSpeed = clamp(seedSpeed, 0.0, 5.0)
        self.seedSize = clamp(seedSize, 0.1, 0.5)
        self.health = 100.0
        self.nutrients = 0.0
    
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
            self.radius = min(self.maxRadius, self.radius + dt * self.growthSpeed * (1.1 - self.rootDepth))
            self.nutrients -= dt * self.growthSpeed
        
        if self.health < 100.0:
            self.health = min(100.0, self.health + dt * self.growthSpeed)
            self.nutrients -= dt * self.growthSpeed
            
            color = (
                int(config.HURT_PLANT_COLOR[0] - config.PLANT_COLOR_DIFF[0] * (self.health / 100.0)),
                int(config.HURT_PLANT_COLOR[1] - config.PLANT_COLOR_DIFF[1] * (self.health / 100.0)),
                int(config.HURT_PLANT_COLOR[2] - config.PLANT_COLOR_DIFF[2] * (self.health / 100.0))
            )
            self.color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        else:
            self.color = f"#{config.HEALTHY_PLANT_COLOR[0]:02x}{config.HEALTHY_PLANT_COLOR[1]:02x}{config.HEALTHY_PLANT_COLOR[2]:02x}"

        sector = self.sectors.get(self.sectorPos)
        if sector.nutrients > 0:
            self.nutrients += dt * self.radius * self.rootDepth * sector.nutrients
        self.nutrients -= dt * self.radius