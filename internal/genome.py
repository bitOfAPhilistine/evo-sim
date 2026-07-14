from internal.color import Color
from internal.funcs import clamp, rand_curve

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
    def __init__(self):
        self.color: Color = Color(rand.randint(0, 255), rand.randint(0, 255), rand.randint(0, 255))
        self.maxRadius: float = rand.uniform(config.MIN_PLANT_RADIUS, config.MAX_PLANT_RADIUS)
        self.growthSpeed: float = rand.uniform(1.0, config.MAX_GROWTH_SPEED)
        self.rootDepth: float = rand.uniform(0.0, 1.0)
        self.seedSpeed: float = rand.uniform(0.0, config.MAX_SEED_SPEED)
        self.lifespan: float = rand.uniform(config.MIN_LIFESPAN, config.MAX_LIFESPAN)
        self.healthThresh: float = rand.uniform(0.0, 100.0)
    
    def __repr__(self):
        return f'''Base Color: {self.color}
    Max Radius: {self.maxRadius:.2f}
    Growth Speed: {self.growthSpeed:.2f}
    Root Depth: {self.rootDepth:.2f}
    Seed Speed: {self.seedSpeed:.2f}
    Lifespan: {self.lifespan:.2f}
    Health Threshold: {self.healthThresh:.2f}'''
    
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
    
    def clamp(self):
        self.maxRadius = clamp(self.maxRadius, config.MIN_PLANT_RADIUS, config.MAX_PLANT_RADIUS)
        self.growthSpeed = clamp(self.growthSpeed, 1.0, config.MAX_GROWTH_SPEED)
        self.rootDepth = clamp(self.rootDepth, 0.0, 1.0)
        self.seedSpeed = clamp(self.seedSpeed, 0.0, config.MAX_SEED_SPEED)
        self.lifespan = clamp(self.lifespan, config.MIN_LIFESPAN, config.MAX_LIFESPAN)
        self.healthThresh = clamp(self.healthThresh, 0.0, 100.0)