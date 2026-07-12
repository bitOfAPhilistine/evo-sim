import random as rand


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def randcurve(min: float, max: float, weight: int = 2) -> float:
    total = 0
    for _ in range(weight):
        total += rand.uniform(min, max)
    return total / weight