from internal.color import Color
from internal.funcs import *
from internal.profiler import profiler

import internal.globals as globals
import random as rand
import copy, config


ranges = {
    'color': 255,
    'maxRadius': config.MAX_PLANT_RADIUS - config.MIN_PLANT_RADIUS,
    'growthSpeed': config.MAX_GROWTH_SPEED - 1.0,
    'rootDepth': 1.0,
    'seedSpeed': config.MAX_SEED_SPEED,
    'lifespan': config.MAX_LIFESPAN - config.MIN_LIFESPAN,
    'healthThresh': 100.0
}

class Genome:
    @profiler
    def __init__(self):
        self.color: Color = Color(
            rand.randint(0, 255),
            rand.randint(0, 255),
            rand.randint(0, 255)
        )
        self.maxRadius: float = rand.uniform(config.MIN_PLANT_RADIUS, config.MAX_PLANT_RADIUS)
        self.growthSpeed: float = rand.uniform(1.0, config.MAX_GROWTH_SPEED)
        self.rootDepth: float = rand.uniform(0.0, 1.0)
        self.seedSpeed: float = rand.uniform(0.0, config.MAX_SEED_SPEED)
        self.lifespan: float = rand.uniform(config.MIN_LIFESPAN, config.MAX_LIFESPAN)
        self.healthThresh: float = rand.uniform(0.0, 100.0)
    
    @profiler
    def readout(self):
        return f'''Base Color: ({self.color.r}, {self.color.g}, {self.color.b})
    Max Radius: {self.maxRadius:.2f}
    Growth Speed: {self.growthSpeed:.2f}
    Root Depth: {self.rootDepth:.2f}
    Seed Speed: {self.seedSpeed:.2f}
    Lifespan: {self.lifespan:.2f}
    Health Threshold: {self.healthThresh:.2f}'''
    
    @profiler
    def mutate(self):
        newGenome = copy.deepcopy(self)

        mutationTrait = rand.choice(list(ranges.keys()))
        
        mutationAmount = rand_curve(-config.MUTATION_FACTOR, config.MUTATION_FACTOR, config.MUTATION_CENTER_WEIGHTING)
        
        if mutationTrait == 'color':
            channel = rand.choice(['r', 'g', 'b'])
            setattr(newGenome.color, channel, getattr(newGenome.color, channel) + ranges['color'] * mutationAmount)
            return newGenome
        
        setattr(newGenome, mutationTrait, getattr(newGenome, mutationTrait) + ranges[mutationTrait] * mutationAmount)

        newGenome.clamp()
        
        return newGenome
    
    @profiler
    def clamp(self):
        self.maxRadius = clamp(self.maxRadius, config.MIN_PLANT_RADIUS, config.MAX_PLANT_RADIUS)
        self.growthSpeed = clamp(self.growthSpeed, 1.0, config.MAX_GROWTH_SPEED)
        self.rootDepth = clamp(self.rootDepth, 0.0, 1.0)
        self.seedSpeed = clamp(self.seedSpeed, 0.0, config.MAX_SEED_SPEED)
        self.lifespan = clamp(self.lifespan, config.MIN_LIFESPAN, config.MAX_LIFESPAN)
        self.healthThresh = clamp(self.healthThresh, 0.0, 100.0)
    
    @profiler
    def dist(self, other) -> tuple[float, str]:
        totalDist = 0.0
        highestDist = ('', 0.0)
        for trait in ranges:
            if trait == 'color':
                colorDist = 0.0
                for channel in ['r', 'g', 'b']:
                    colorDist += abs(getattr(self.color, channel) - getattr(other.color, channel)) / ranges['color'] / 3
                
                totalDist += colorDist
                highestDist = ('color', colorDist)

                continue
            
            dist = abs(getattr(self, trait) - getattr(other, trait)) / ranges[trait]
            totalDist += dist

            if dist > highestDist[1]:
                highestDist = (trait, dist)

        return totalDist, highestDist[0]