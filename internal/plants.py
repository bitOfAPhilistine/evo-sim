import math
from tkinter import Canvas
from internal.vector2 import Vector2, HashVector2
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
    def __init__(self, world: World, pos: Vector2, genome: Genome = None, isMutant = False):
        
        self.genome = Genome() if genome is None else genome

        super().__init__(world, pos, self.genome.maxRadius * config.SEED_SIZE_FACTOR, self.genome.color, Color(255, 255, 255), 0)

        self.isMutant = isMutant
        self.updateableIndex = world.updateable.add(self)
        self.sectorOverlaps = world.sectors.get_overlap(pos.hash(), self.radius)

        self.baseColor = self.genome.color
        self.maxRadius = clamp(self.genome.maxRadius, config.MIN_PLANT_RADIUS, config.MAX_PLANT_RADIUS)
        self.growthSpeed = clamp(self.genome.growthSpeed, 1.0, config.MAX_GROWTH_SPEED)
        self.rootDepth = clamp(self.genome.rootDepth, 0.0, 1.0)
        self.seedSpeed = clamp(self.genome.seedSpeed, 0.0, config.MAX_SEED_SPEED)
        self.lifespan = clamp(self.genome.lifespan, config.MIN_LIFESPAN, config.MAX_LIFESPAN)
        self.healthThresh = clamp(self.genome.healthThresh, 0.0, 100.0)
        
        self.photoFactor = sum(map(lambda mine, opt: ((256 - mine) / (256 - opt)) ** 2, self.baseColor, config.OPTIMAL_PLANT_COLOR)) / 3
        self.growthRate = self.maxRadius * 0.9 / (self.lifespan / self.growthSpeed * (1.5 - self.rootDepth))
        self.seedSize = self.maxRadius * config.SEED_SIZE_FACTOR
        self.seedForce = self.seedSpeed * (self.seedSize ** 2 * math.pi)
        self.seedCost = math.log10(self.seedSpeed) * (self.seedSize ** 2 * math.pi)

        self.lifeLeft = self.lifespan
        self.health = 100.0
        self.nutrients = 0.0
        self.maxNutrients = self.area
    
    def __repr__(self):
        return f'''Plant:
    Position: {self.pos}
    Color: {self.color}
    Radius: {self.radius:.2f}
    Area: {self.area:.2f}
    Is Mutant: {self.isMutant}
    ---Genome---
    {self.genome}
    ---Derived---
    Photo Factor: {self.photoFactor:.2f}
    Growth Rate: {self.growthRate:.2f}
    Seed Size: {self.seedSize:.2f}
    Seed Force: {self.seedForce:.2f}
    Seed Cost: {self.seedCost:.2f}
    ---Dynamic---
    Time Left: {self.lifeLeft:.2f}
    Time Until Maturity: {((self.maxRadius - self.radius) / self.growthRate):.2f}
    Health: {self.health:.2f}
    Nutrients: {self.nutrients:.2f}/{self.maxNutrients:.2f}'''
    
    def delete(self, canvas: Canvas):
        super().delete(canvas)
        if self.updateableIndex is not None:
            self.world.updateable.remove(self.updateableIndex)

    def update(self, dt, canvas: Canvas):
        self.lifeLeft -= dt
        self.nutrients -= dt * self.area

        if self.lifeLeft <= 0.0:
            self.health += self.lifeLeft * dt

        if self.nutrients < 0.0:
            self.health += self.nutrients / self.area * 10.0
            self.nutrients = 0.0
        
        if self.photoFactor > 1.0:
            self.health -= (self.photoFactor - 1.0) * self.radius * dt

        if self.health <= 0.0:
            if self.nutrients > 0.0:
                self.world.sectors.get(self.sectorPos).nutrients += self.nutrients / self.world.sectors.sectorArea
            self.world.sectors.get(self.sectorPos).nutrients += self.area / self.world.sectors.sectorArea
            self.delete(canvas)
            return
        elif self.health < 100.0:
            self.health = min(100.0, self.health + dt * self.growthSpeed)
            self.nutrients -= dt * self.growthSpeed

            self.strokeWidth = math.floor(self.radius * (1.0 - (self.health / 100.0)))
        
        if self.health >= self.healthThresh:
            if self.radius < self.maxRadius:
                self.radius = min(self.maxRadius, self.radius + dt * self.growthRate)
                self.maxNutrients = self.area
                self.sectorOverlaps = self.world.sectors.get_overlap(self.pos.hash(), self.radius, 8 - math.floor(math.log2(dt / config.TARGET_FRAMERATE)))
                self.nutrients -= dt * self.growthRate
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

        if self.nutrients < self.maxNutrients:
            nutrientsWanted = max(0, min(self.maxNutrients - self.nutrients, dt * self.area * self.photoFactor))
            
            if len(self.sectorOverlaps) == 0:
                print("Error: plant lacks sectorOverlaps, recalculating...")
                print(f"{self}")
            if isinstance(self.sectorOverlaps[0], tuple):
                overlaps = list(self.sectorOverlaps)
                rand.shuffle(overlaps)
            else:
                overlaps = [self.sectorOverlaps]

            for so in overlaps:
                try:
                    sector = self.world.sectors.get(so[0])
                except IndexError:
                    continue
                available = 0.0

                if sector.nutrients > 1.0 - self.rootDepth:
                    available = self.world.sectors.sectorArea * so[1] * max(0, sector.nutrients + self.rootDepth - 1.0) * dt
                
                taken = max(0, min(available, nutrientsWanted))
                sector.nutrients -= taken / self.world.sectors.sectorArea
                self.nutrients += taken * config.PLANT_NUTRIENT_EFFICIENCY
                nutrientsWanted -= taken * config.PLANT_NUTRIENT_EFFICIENCY

                if nutrientsWanted <= 0.0 or self.nutrients >= self.maxNutrients:
                    self.nutrients = min(self.nutrients, self.maxNutrients)
                    break


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
    Radius: {self.radius:.2f}
    Velocity: {self.velocity}
    Is Mutant: {self.isMutant}
    ---Genome---
    {self.genome}'''

    def update(self, dt, canvas: Canvas):
        super().update(dt, canvas)

        if self.velocity.magnitude() <= 0.5:
            Plant(
                world=self.world,
                pos=self.pos.copy(),
                genome=self.genome,
                isMutant=self.isMutant
            )
            self.delete(canvas)