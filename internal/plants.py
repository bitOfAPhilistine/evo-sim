import math
from tkinter import Canvas
from internal.vector2 import Vector2
from internal.smartList import SmartList
from internal.world import Sectors, World
from internal.objects import GameObject, PhysicsObject
from internal.color import Color
from internal.clamp import clamp

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
                color: Color,
                maxRadius: float,
                growthSpeed: float,
                rootDepth: float,
                seedSpeed: float,
                lifespan: float):
        
        super().__init__(world, pos, maxRadius * config.SEED_SIZE_FACTOR, color, Color(255, 255, 255), 0)

        self.updateableIndex = world.updateable.add(self)
        self.baseColor = color
        self.maxRadius = clamp(maxRadius, 1.0, 100.0)
        self.growthSpeed = clamp(growthSpeed, 1.0, 5.0)
        self.rootDepth = clamp(rootDepth, 0.0, 1.0)
        self.seedSpeed = clamp(seedSpeed, 0.0, 100.0)
        self.lifespan = clamp(lifespan, 30.0, 120.0)
        self.lifeLeft = self.lifespan
        self.health = 100.0
        self.nutrients = 0.0
        self.photoFactor = sum(map(lambda mine, opt: ((256 - mine) / (256 - opt)) ** 2, self.baseColor, config.OPTIMAL_PLANT_COLOR)) / 3
        self.growthRate = self.maxRadius * 0.9 / (self.lifespan / self.growthSpeed * (1.5 - self.rootDepth))
        self.seedSize = self.maxRadius * config.SEED_SIZE_FACTOR
        self.seedForce = self.seedSpeed * (self.seedSize ** 2 * math.pi)
        self.seedCost = math.log10(self.seedSpeed) * (self.seedSize ** 2 * math.pi)
    
    def __repr__(self):
        return f'''Plant:
    Position: {self.pos}
    Color: {self.baseColor}
    Radius: {self.radius}
    Max Radius: {self.maxRadius}
    Growth Speed: {self.growthSpeed}
    Root Depth: {self.rootDepth}
    Seed Speed: {self.seedSpeed}
    Lifespan: {self.lifespan}
    Time Left: {self.lifeLeft}
    Health: {self.health}
    Nutrients: {self.nutrients}
    Photo Factor: {self.photoFactor}
    Growth Rate: {self.growthRate}
    Seed Size: {self.seedSize}
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
        
        if self.photoFactor > 1.0:
            self.health -= (self.photoFactor - 1.0) * self.radius * dt

        if self.health <= 0.0:
            if self.nutrients > 0.0:
                self.world.sectors.get(self.sectorPos).nutrients += self.nutrients * config.SECTOR_RETURN_FACTOR
            self.delete(canvas)
            return
        elif self.health < 100.0:
            self.health = min(100.0, self.health + dt * self.growthSpeed)
            self.nutrients -= dt * self.growthSpeed

            self.strokeWidth = math.floor(self.radius * (1.0 - (self.health / 100.0)))
        if self.health > 90.0:
            if self.radius < self.maxRadius:
                self.radius = min(self.maxRadius, self.radius + dt * self.growthRate)
                self.nutrients -= dt * self.growthSpeed
            elif self.nutrients > self.seedCost and rand.random() < dt:
                self.nutrients -= self.seedCost
                angle = rand.uniform(0, 2 * math.pi)
                distance = self.radius + self.seedSize
                offset = Vector2(distance * math.cos(angle), distance * math.sin(angle))
                seed = Seed(
                    world=self.world,
                    pos=self.pos + offset,
                    radius=self.seedSize,
                    color=self.baseColor,
                    maxRadius=self.maxRadius,
                    growthSpeed=self.growthSpeed,
                    rootDepth=self.rootDepth,
                    seedSpeed=self.seedSpeed,
                    lifespan=self.lifespan
                )

                if rand.random() < config.MUTATION_CHANCE:
                    mutationTrait = rand.randint(0, 7)
                    mutationAmount = randcurve(1.0 - config.MUTATION_FACTOR, 1.0 + config.MUTATION_FACTOR, config.MUTATION_CENTER_WEIGHTING)

                    match mutationTrait:
                        case 0:
                            seed.baseColor.r = int(seed.baseColor.r * mutationAmount)
                        case 1:
                            seed.baseColor.g = int(seed.baseColor.g * mutationAmount)
                        case 2:
                            seed.baseColor.b = int(seed.baseColor.b * mutationAmount)
                        case 3:
                            seed.maxRadius = seed.maxRadius * mutationAmount
                        case 4:
                            seed.growthSpeed = seed.growthSpeed * mutationAmount
                        case 5:
                            seed.rootDepth = seed.rootDepth * mutationAmount
                        case 6:
                            seed.seedSpeed = seed.seedSpeed * mutationAmount
                        case 7:
                            seed.lifespan = seed.lifespan * mutationAmount

                seed.apply_force(offset.normalize().scale(self.seedForce))

        sector = self.world.sectors.get(self.sectorPos)
        if sector.nutrients > 0:
            self.nutrients += dt * self.radius * self.rootDepth * self.photoFactor * sector.nutrients * config.PLANT_NUTRIENT_EFFICIENCY
            sector.nutrients -= dt * self.radius * self.rootDepth * sector.nutrients * config.SECTOR_CONSUMPTION_FACTOR
        self.nutrients -= dt * self.radius


class Seed(PhysicsObject):
    def __init__(self, world: World, pos: Vector2,
                radius: float,
                color: Color,
                maxRadius: float,
                growthSpeed: float,
                rootDepth: float,
                seedSpeed: float,
                lifespan: float):
        
        super().__init__(world, pos, radius, Color(145, 45, 30), math.pi * radius ** 2, config.SEED_DRAG)

        self.baseColor = color
        self.maxRadius = maxRadius
        self.growthSpeed = growthSpeed
        self.rootDepth = rootDepth
        self.seedSpeed = seedSpeed
        self.lifespan = lifespan
    
    def __repr__(self):
        return f'''Seed:
    Position: {self.pos}
    Radius: {self.radius}
    Color: {self.baseColor}
    Max Radius: {self.maxRadius}
    Growth Speed: {self.growthSpeed}
    Root Depth: {self.rootDepth}
    Seed Speed: {self.seedSpeed}'''

    def update(self, dt, canvas: Canvas):
        super().update(dt, canvas)

        try:
            if self.velocity.magnitude() <= 0.1:
                Plant(
                    world=self.world,
                    pos=self.pos.copy(),
                    color=self.baseColor,
                    maxRadius=self.maxRadius,
                    growthSpeed=self.growthSpeed,
                    rootDepth=self.rootDepth,
                    seedSpeed=self.seedSpeed,
                    lifespan=self.lifespan
                )
                self.delete(canvas)
        except OverflowError:
            print(f"Overflow error in seed update: {self}")
            self.delete(canvas)