import math
from tkinter import Canvas
from internal.vector2 import Vector2
from internal.smartList import SmartList
from internal.world import Sectors, World, clamp
from internal.objects import GameObject, PhysicsObject

import random as rand
import config


def randcurve(min: float, max: float, weight: int = 2) -> float:
    """Returns a random float between min and max, with a curve towards the middle"""
    total = 0
    for _ in range(weight):
        total += rand.uniform(min, max)
    return total / weight

class Plant(GameObject):
    def __init__(self, world: World, pos: Vector2,
                maxRadius: float,
                growthSpeed: float,
                rootDepth: float,
                seedSpeed: float,
                lifespan: float):
        
        super().__init__(world, pos, maxRadius * config.SEED_SIZE_FACTOR, config.HEALTHY_PLANT_COLOR)

        self.updateableIndex = world.updateable.add(self)
        self.maxRadius = clamp(maxRadius, 1.0, 50.0)
        self.growthSpeed = clamp(growthSpeed, 0.0, 2.0)
        self.rootDepth = clamp(rootDepth, 0.0, 1.0)
        self.seedSpeed = clamp(seedSpeed, 0.0, 100.0)
        self.lifespan = clamp(lifespan, 30.0, 120.0)
        self.lifeLeft = self.lifespan
        self.health = 100.0
        self.nutrients = 0.0
        self.seedForce = self.seedSpeed * ((self.maxRadius * config.SEED_SIZE_FACTOR) ** 2 * math.pi)
        self.seedCost = math.log10(self.seedSpeed) * ((self.maxRadius * config.SEED_SIZE_FACTOR) ** 2 * math.pi)
    
    def __repr__(self):
        return f'''Plant:
    Position: {self.pos}
    Radius: {self.radius}
    Max Radius: {self.maxRadius}
    Growth Speed: {self.growthSpeed}
    Root Depth: {self.rootDepth}
    Seed Speed: {self.seedSpeed}
    Lifespan: {self.lifespan}
    Time Left: {self.lifeLeft}
    Health: {self.health}
    Nutrients: {self.nutrients}
    Seed Force: {self.seedForce}
    Seed Cost: {self.seedCost}'''
    
    def delete(self, canvas: Canvas):
        super().delete(canvas)
        if self.updateableIndex is not None:
            self.world.updateable.remove(self.updateableIndex)

    def update(self, dt, canvas: Canvas):
        self.lifeLeft -= dt
        if self.lifeLeft <= 0.0:
            self.health += self.lifeLeft * dt

        if self.nutrients < 0.0:
            self.health += self.nutrients
            self.nutrients = 0.0
        
        if self.health <= 0.0:
            if self.nutrients > 0.0:
                self.world.sectors.get(self.sectorPos).nutrients += self.nutrients * config.SECTOR_RETURN_FACTOR
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
        if self.health > 90.0:
            self.color = f"#{config.HEALTHY_PLANT_COLOR[0]:02x}{config.HEALTHY_PLANT_COLOR[1]:02x}{config.HEALTHY_PLANT_COLOR[2]:02x}"
            
            if self.radius < self.maxRadius:
                self.radius = min(self.maxRadius, self.radius + dt * self.growthSpeed * (1.1 - self.rootDepth))
                self.nutrients -= dt * self.growthSpeed
            elif self.nutrients > self.seedCost and rand.random() < dt:
                self.nutrients -= self.seedCost
                angle = rand.uniform(0, 2 * math.pi)
                distance = self.radius + self.maxRadius * config.SEED_SIZE_FACTOR
                offset = Vector2(distance * math.cos(angle), distance * math.sin(angle))
                seed = Seed(
                    world=self.world,
                    pos=self.pos + offset,
                    radius=(self.maxRadius * config.SEED_SIZE_FACTOR),
                    maxRadius=self.maxRadius,
                    growthSpeed=self.growthSpeed,
                    rootDepth=self.rootDepth,
                    seedSpeed=self.seedSpeed,
                    lifespan=self.lifespan
                )

                if rand.random() < config.MUTATION_CHANCE:
                    mutation = rand.randint(0, 4)
                    match mutation:
                        case 0:
                            seed.maxRadius = seed.maxRadius * randcurve(0.5, 1.5, 3)
                        case 1:
                            seed.growthSpeed = seed.growthSpeed * randcurve(0.5, 1.5, 3)
                        case 2:
                            seed.rootDepth = seed.rootDepth * randcurve(0.5, 1.5, 3)
                        case 3:
                            seed.seedSpeed = seed.seedSpeed * randcurve(0.5, 1.5, 3)
                        case 4:
                            seed.lifespan = seed.lifespan * randcurve(0.5, 1.5, 3)
                
                seed.apply_force(offset.normalize().scale(self.seedForce))

        sector = self.world.sectors.get(self.sectorPos)
        if sector.nutrients > 0:
            self.nutrients += dt * self.radius * self.rootDepth * sector.nutrients * config.PLANT_NUTRIENT_EFFICIENCY
            sector.nutrients -= dt * self.radius * self.rootDepth * sector.nutrients * config.SECTOR_CONSUMPTION_FACTOR
        self.nutrients -= dt * self.radius


class Seed(PhysicsObject):
    def __init__(self, world: World, pos: Vector2,
                radius: float,
                maxRadius: float,
                growthSpeed: float,
                rootDepth: float,
                seedSpeed: float,
                lifespan: float):
        
        super().__init__(world, pos, radius, "brown", math.pi * radius ** 2, config.SEED_DRAG)

        self.maxRadius = maxRadius
        self.growthSpeed = growthSpeed
        self.rootDepth = rootDepth
        self.seedSpeed = seedSpeed
        self.lifespan = lifespan
    
    def __repr__(self):
        return f'''Seed:
    Position: {self.pos}
    Radius: {self.radius}
    Max Radius: {self.maxRadius}
    Growth Speed: {self.growthSpeed}
    Root Depth: {self.rootDepth}
    Seed Speed: {self.seedSpeed}'''

    def update(self, dt, canvas: Canvas):
        super().update(dt, canvas)

        if self.velocity.magnitude() <= 0.1:
            Plant(
                world=self.world,
                pos=self.pos.copy(),
                maxRadius=self.maxRadius,
                growthSpeed=self.growthSpeed,
                rootDepth=self.rootDepth,
                seedSpeed=self.seedSpeed,
                lifespan=self.lifespan
            )
            self.delete(canvas)