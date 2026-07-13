from internal.vector2 import Vector2, HashVector2

import random as rand
import functools


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def rand_curve(min: float, max: float, weight: int = 2) -> float:
    total = 0
    for _ in range(weight):
        total += rand.uniform(min, max)
    return total / weight

def check_point_rect(point: Vector2, minCorner: Vector2, maxCorner: Vector2) -> bool:
    return minCorner <= point <= maxCorner

@functools.cache
def check_point_circle(point: HashVector2, center: HashVector2, radius: float) -> bool:
    return (point.x - center.x) ** 2 + (point.y - center.y) ** 2 <= radius ** 2

@functools.cache
def check_rect_circle(minCorner: HashVector2, maxCorner: HashVector2, center: HashVector2, radius: float) -> bool:
    closest = Vector2(max(minCorner.x, min(center.x, maxCorner.x)), max(minCorner.y, min(center.y, maxCorner.y)))

    dif = center - closest

    return dif.x ** 2 + dif.y ** 2 <= radius ** 2

# Recursive internal function to figure out overlap
@functools.cache
def grid_border_search(outerCorners: list[list[HashVector2, bool]], pos: HashVector2, radius: float, dividedGridSizes: list[int], currentPrecision: int = 0) -> float:
    cornerOverlap = len(list(filter(lambda x: x[1], outerCorners)))
    
    # Check if given section is fully overlapping and return full value if so
    if cornerOverlap == 4:
        return 1.0 / dividedGridSizes[currentPrecision]
    
    # Check if no corners overlap and if circle can't intersect regardless, return 0.0 if so
    if cornerOverlap == 0 and not check_rect_circle(outerCorners[0][0].hash(), outerCorners[3][0].hash(), pos, radius):
        return 0.0
    
    # Check if at max precision and return proportional value if so
    if currentPrecision + 1 == len(dividedGridSizes):
        return (1.0 / dividedGridSizes[currentPrecision]) * (cornerOverlap / 4.0)
    
    # Define inner + corners for subgrid and check
    innerCorners = [
        [outerCorners[0][0].middle(outerCorners[1][0]), False],
        [outerCorners[0][0].middle(outerCorners[2][0]), False],
        [outerCorners[0][0].middle(outerCorners[3][0]), False],
        [outerCorners[1][0].middle(outerCorners[3][0]), False],
        [outerCorners[2][0].middle(outerCorners[3][0]), False]
    ]
    innerCorners = list(map(lambda x: [x[0].hash(), check_point_circle(x[0].hash(), pos, radius)], innerCorners))
    
    subgrid = [
        [
            outerCorners[0], innerCorners[0],
            innerCorners[1], innerCorners[2]
        ],
        [
            innerCorners[0], outerCorners[1],
            innerCorners[2], innerCorners[3]
        ],
        [
            innerCorners[1], innerCorners[2],
            outerCorners[2], innerCorners[4]
        ],
        [
            innerCorners[2], innerCorners[3],
            innerCorners[4], outerCorners[3]
        ]
    ]

    # Pass each sub-section into the next layer down then add all the return values together
    return float(sum(map(lambda x: grid_border_search(x, pos, radius, dividedGridSizes, currentPrecision + 1), subgrid)))