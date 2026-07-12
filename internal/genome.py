from internal.color import Color
from internal.funcs import clamp, randcurve

import random as rand
import copy, config


ranges = {
    'color': 255,
    'maxRadius': config.MAX_PLANT_RADIUS - config.MIN_PLANT_RADIUS,
    'growthSpeed': config.MAX_GROWTH_SPEED - 1.0,
    'rootDepth': 1.0,
    'seedSpeed': config.MAX_SEED_SPEED,
    'lifespan': config.MAX_LIFESPAN - config.MIN_LIFESPAN
}

class Genome:
    def __init__(self):
        self.color: Color = Color(rand.randint(0, 255), rand.randint(0, 255), rand.randint(0, 255))
        self.maxRadius: float = rand.uniform(config.MIN_PLANT_RADIUS, config.MAX_PLANT_RADIUS)
        self.growthSpeed: float = rand.uniform(1.0, config.MAX_GROWTH_SPEED)
        self.rootDepth: float = rand.uniform(0.0, 1.0)
        self.seedSpeed: float = rand.uniform(0.0, config.MAX_SEED_SPEED)
        self.lifespan: float = rand.uniform(config.MIN_LIFESPAN, config.MAX_LIFESPAN)
    
    def mutate(self):
        newGenome = copy.deepcopy(self)

        mutationTrait = rand.choice(list(ranges.keys()))
        
        mutationAmount = randcurve(-config.MUTATION_FACTOR, config.MUTATION_FACTOR, config.MUTATION_CENTER_WEIGHTING)
        
        if mutationTrait == 'color':
            channel = rand.randint(0, 2)
            newGenome.color[channel] = newGenome.color[channel] + mutationAmount * ranges['color']
        setattr(newGenome, mutationTrait, getattr(newGenome, mutationTrait) + ranges[mutationTrait] * mutationAmount)
        
        return newGenome