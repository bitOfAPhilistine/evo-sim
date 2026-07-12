import math
from tkinter import Canvas
from internal.vector2 import Vector2
from internal.smartList import SmartList
from internal.world import Sectors, World
from internal.objects import GameObject, PhysicsObject
from internal.genome import Genome
from internal.color import Color
from internal.funcs import clamp

import random as rand
import config
import copy


class Plant(GameObject):
    def __init__(self, world: World, pos: Vector2, genome: Genome = None):
        
        self.genome = Genome() if genome is None else genome

        super().__init__(world, pos, self.genome.maxRadius * config.SEED_SIZE_FACTOR, self.genome.color, Color(255, 255, 255), 0)

        self.updateableIndex = world.updateable.add(self)
        self.baseColor = self.genome.color
        self.maxRadius = clamp(self.genome.maxRadius, config.MIN_PLANT_RADIUS, config.MAX_PLANT_RADIUS)
        self.growthSpeed = clamp(self.genome.growthSpeed, 1.0, config.MAX_GROWTH_SPEED)
        self.rootDepth = clamp(self.genome.rootDepth, 0.0, 1.0)
        self.seedSpeed = clamp(self.genome.seedSpeed, 0.0, config.MAX_SEED_SPEED)
        self.lifespan = clamp(self.genome.lifespan, config.MIN_LIFESPAN, config.MAX_LIFESPAN)
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
    Genome: {self.genome.__hash__()}
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
                    genome=self.genome
                )

                seed.apply_force(offset.normalize().scale(self.seedForce))

        sector = self.world.sectors.get(self.sectorPos)
        if sector.nutrients > 0:
            self.nutrients += dt * self.radius * self.rootDepth * self.photoFactor * sector.nutrients * config.PLANT_NUTRIENT_EFFICIENCY
            sector.nutrients -= dt * self.radius * self.rootDepth * sector.nutrients * config.SECTOR_CONSUMPTION_FACTOR
        self.nutrients -= dt * self.radius


class Seed(PhysicsObject):
    def __init__(self, world: World, pos: Vector2, radius: float, genome: Genome):
        super().__init__(world, pos, radius, Color(145, 45, 30), math.pi * radius ** 2, config.SEED_DRAG)

        self.isMutant = rand.random() < config.MUTATION_CHANCE
        self.genome: Genome = None
        if self.isMutant:
            self.genome = genome.mutate()
        else:
            self.genome = genome
        
        if self.genome == None:
            raise Exception("seed lacks genome")
    
    def __repr__(self):
        return f'''Seed:
    Position: {self.pos}
    Radius: {self.radius}
    Is Mutant: {self.isMutant}
    Genome: {self.genome.__hash__()}'''

    def update(self, dt, canvas: Canvas):
        super().update(dt, canvas)

        if self.velocity.magnitude() <= 0.5:
            Plant(
                world=self.world,
                pos=self.pos.copy(),
                genome=self.genome
            )
            self.delete(canvas)