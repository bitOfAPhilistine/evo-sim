import math
from tkinter import Canvas
from internal.vector2 import Vector2
from internal.smartList import SmartList
from internal.world import Sectors, World, clamp
from internal.objects import GameObject, PhysicsObject

import random as rand
import config


class Plant(GameObject):
    def __init__(self, world: World, pos: Vector2,
                maxRadius: float,
                growthSpeed: float,
                rootDepth: float,
                seedSpeed: float):
        
        super().__init__(world, pos, maxRadius / 5, config.HEALTHY_PLANT_COLOR)

        self.updateableIndex = world.updateable.add(self)
        self.maxRadius = clamp(maxRadius, 1.0, 50.0)
        self.growthSpeed = clamp(growthSpeed, 0.0, 2.0)
        self.rootDepth = clamp(rootDepth, 0.0, 1.0)
        self.seedSpeed = clamp(seedSpeed, 0.0, 10.0)
        self.health = 100.0
        self.nutrients = 0.0
    
    def delete(self, canvas: Canvas):
        super().delete(canvas)
        if self.updateableIndex is not None:
            self.world.updateable.remove(self.updateableIndex)

    def update(self, dt, canvas: Canvas):
        if self.nutrients < 0.0:
            self.health += self.nutrients
            self.nutrients = 0.0
        
        if self.health <= 0.0:
            self.delete(canvas)
            return
        elif self.health < 100.0:
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
            seedForce = self.seedSpeed * (self.maxRadius / 10) ** 2 * math.pi
            seedCost = seedForce * 10.0

            if self.radius < self.maxRadius:
                self.radius = min(self.maxRadius, self.radius + dt * self.growthSpeed * (1.1 - self.rootDepth))
                self.nutrients -= dt * self.growthSpeed
            elif self.nutrients > seedCost and rand.random() < dt:
                self.nutrients -= seedCost
                angle = rand.uniform(0, 2 * math.pi)
                distance = self.radius + self.maxRadius / 10
                offset = Vector2(distance * math.cos(angle), distance * math.sin(angle))
                seed = Seed(
                    world=self.world,
                    pos=self.pos + offset,
                    radius=(self.maxRadius / 10),
                    maxRadius=self.maxRadius,
                    growthSpeed=self.growthSpeed,
                    rootDepth=self.rootDepth,
                    seedSpeed=self.seedSpeed,
                )
                seed.apply_force(offset.normalize().scale(seedForce))

        sector = self.world.sectors.get(self.sectorPos)
        if sector.nutrients > 0:
            self.nutrients += dt * self.radius * self.rootDepth * sector.nutrients * 10
            sector.nutrients -= dt * self.radius / 50 * self.rootDepth * sector.nutrients / 10
        self.nutrients -= dt * self.radius


class Seed(PhysicsObject):
    def __init__(self, world: World, pos: Vector2,
                radius: float,
                maxRadius: float,
                growthSpeed: float,
                rootDepth: float,
                seedSpeed: float):
        
        super().__init__(world, pos, radius, "brown", math.pi * radius ** 2, 0.1)

        self.maxRadius = maxRadius
        self.growthSpeed = growthSpeed
        self.rootDepth = rootDepth
        self.seedSpeed = seedSpeed

    def update(self, dt, canvas: Canvas):
        super().update(dt, canvas)

        if self.velocity.magnitude() <= 0.1:
            Plant(
                world=self.world,
                pos=self.pos.copy(),
                maxRadius=self.maxRadius,
                growthSpeed=self.growthSpeed,
                rootDepth=self.rootDepth,
                seedSpeed=self.seedSpeed
            )
            self.delete(canvas)