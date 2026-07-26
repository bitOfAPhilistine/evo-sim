import math
from tkinter import Canvas
from internal.vector2 import Vector2
from internal.smartList import SmartList
from internal.world import Sectors, World, Species
from internal.objects import GameObject, PhysicsObject
from internal.genome import Genome
from internal.color import Color
from internal.funcs import *
from internal.profiler import profiler

import internal.globals as globals
import random as rand
import config, time


class Plant(GameObject):
    @profiler
    def __init__(self, world: World, pos: Vector2, genome: Genome = None, isMutant = False, species = None):
        
        self.genome = Genome() if genome is None else genome

        super().__init__(world, pos, self.genome.maxRadius * config.SEED_SIZE_FACTOR, self.genome.color)

        self.isMutant = isMutant
        self.species = species if species != None else world.create_species(self.genome, True)
        self.species.memberCount += 1
        self.updateableIndex = world.updateable.add(self)
        self.lastUpdated = time.time()
        self.sectorOverlaps = [1.0 / len(self.sectors) for _ in self.sectors]
        self.queued = False
        world.request_overlaps(self)
        self.world.plantCount += 1

        self.baseColor = self.genome.color
        self.maxRadius = self.genome.maxRadius
        self.growthSpeed = self.genome.growthSpeed
        self.rootDepth = self.genome.rootDepth
        self.seedSpeed = self.genome.seedSpeed
        self.lifespan = self.genome.lifespan
        self.healthThresh = self.genome.healthThresh
        
        self.photoFactor = sum(map(lambda mine, opt: (256 - mine) / (256 - opt), self.baseColor, Color(*config.OPTIMAL_PLANT_COLOR))) / 3
        self.growthRate = self.maxRadius * 0.9 / (self.lifespan / (self.growthSpeed * (1.5 - self.rootDepth)))
        self.seedSize = self.maxRadius * config.SEED_SIZE_FACTOR
        self.seedForce = self.seedSpeed * (self.seedSize ** 2 * math.pi) * config.SEED_DENSITY
        self.seedCost = (math.log10(self.seedSpeed) * (self.seedSize ** 2 * math.pi)) if self.seedSpeed > 0.0 else 0.0

        self.lifeLeft = self.lifespan
        self.health = 100.0
        self.nutrients = 0.0
        self.maxNutrients = self.area
    
    @profiler
    def readout(self):
        return f'''Plant:
    Position: {self.pos.x:.2f}, {self.pos.y:.2f}
    Radius: {self.radius:.2f}
    Area: {self.area:.2f}
    Sector Overlaps:
        {'\n        '.join(list(map(lambda sector, overlap: f"({sector.sectorPos.x:.0f}, {sector.sectorPos.y:.0f}): {overlap:.3f}", self.sectors, self.sectorOverlaps)))}
    Is Mutant: {self.isMutant}
    Species: {self.species.index}
    ---Genome---
    {self.genome.readout()}
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
    
    @profiler
    def delete(self, canvas: Canvas):
        super().delete(canvas)
        if self.updateableIndex is not None:
            self.world.updateable.remove(self.updateableIndex)
        
        self.species.sub1()
        self.world.plantCount -= 1

    @profiler
    def update_sectors(self):
        super().update_sectors()

        if len(self.sectors) == 1:
            self.sectorOverlaps = [1.0]
            return
        
        if not self.queued:
            self.world.request_overlaps(self)
        
        if len(self.sectorOverlaps) != len(self.sectors):
            self.sectorOverlaps = [1.0 / len(self.sectors) for _ in self.sectors]

    @profiler
    def update(self, canvas: Canvas):
        dt = min(config.TARGET_FRAMERATE * 10.0, time.time() - self.lastUpdated)

        if self.nutrients < self.maxNutrients:
            nutrientsWanted = max(0, min(self.maxNutrients - self.nutrients, dt * self.area * self.photoFactor))

            for sector, overlap in list(zip(self.sectors, self.sectorOverlaps, strict=True)):
                available = 0.0

                if sector.nutrients > 1.0 - self.rootDepth:
                    available = self.world.sectors.sectorArea * overlap * max(0, sector.nutrients + self.rootDepth - 1.0) * dt
                
                taken = max(0, min(available, nutrientsWanted))
                sector.nutrients -= taken / self.world.sectors.sectorArea
                self.nutrients += taken * config.PLANT_NUTRIENT_EFFICIENCY
                nutrientsWanted -= taken * config.PLANT_NUTRIENT_EFFICIENCY

                if nutrientsWanted <= 0.0 or self.nutrients >= self.maxNutrients:
                    self.nutrients = min(self.nutrients, self.maxNutrients)
                    break
        
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
            for sector, overlap in zip(self.sectors, self.sectorOverlaps, strict=True):
                if self.nutrients > 0.0:
                    sector.nutrients += self.nutrients * overlap / self.world.sectors.sectorArea
                sector.nutrients += self.area * overlap / self.world.sectors.sectorArea

            self.delete(canvas)
            return
        elif self.health < 100.0:
            self.health = min(100.0, self.health + dt * self.growthSpeed)
            self.nutrients -= dt * self.growthSpeed
        
        if self.health >= self.healthThresh:
            if self.radius < self.maxRadius:
                self.radius = min(self.maxRadius, self.radius + dt * self.growthRate)
                self.maxNutrients = self.area
                
                self.nutrients -= dt * (self.growthRate ** 2 * math.pi)
            elif self.nutrients > self.seedCost and rand.random() < 1.0 / (self.world.seedCount + 1):
                self.nutrients -= self.seedCost
                angle = rand.uniform(0, 2 * math.pi)
                distance = self.radius + self.seedSize
                offset = Vector2(distance * math.cos(angle), distance * math.sin(angle))

                if self.isMutant:
                    dists = self.genome.dist(self.species.genome)
                    if dists[0] > 0.1:
                        newSpecies = self.world.create_species(self.genome, False)
                        newSpecies.parent = self.species
                        self.species.memberCount -= 1
                        newSpecies.memberCount += 1

                        print(f"Species {self.species.index} has speciated into {newSpecies.index}, main difference: {dists[1]}")

                        self.species = newSpecies
                    self.isMutant = False

                seed = Seed(
                    world=self.world,
                    pos=self.pos + offset,
                    radius=self.seedSize,
                    genome=self.genome,
                    species=self.species
                )

                seed.apply_force(offset.normalize().scale(self.seedForce))
        
        self.strokeColor.r = int(255 - self.health / 100.0 * 255)
        self.strokeColor.g = int(self.nutrients / self.maxNutrients * 255)

        self.lastUpdated = time.time()


class Seed(PhysicsObject):
    @profiler
    def __init__(self, world: World, pos: Vector2, radius: float, genome: Genome, species: Species):
        super().__init__(world, pos, radius, Color(145, 45, 30), config.SEED_DENSITY, config.SEED_DRAG)

        self.world.seedCount += 1

        self.isMutant = rand.random() < config.MUTATION_CHANCE
        self.genome: Genome = None
        self.species = species
        if self.isMutant:
            self.genome = genome.mutate()
        else:
            self.genome = genome
        
        if self.genome == None:
            raise Exception("seed lacks genome")
    
    @profiler
    def readout(self):
        return f'''Seed:
    Position: {self.pos}
    Radius: {self.radius:.2f}
    Velocity: {self.velocity}
    Is Mutant: {self.isMutant}
    Species: {self.species}
    ---Genome---
    {self.genome.readout()}'''

    @profiler
    def delete(self, canvas: Canvas):
        super().delete(canvas)

        self.world.seedCount -= 1

    @profiler
    def update(self, canvas: Canvas):
        super().update(canvas)

        if self.velocity.magnitude() <= 0.5:
            Plant(
                world=self.world,
                pos=self.pos.copy(),
                genome=self.genome,
                isMutant=self.isMutant,
                species=self.species
            )
            self.delete(canvas)