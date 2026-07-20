from internal.vector2 import Vector2
from internal.profiler import profiler

import random as rand
import functools, config


@profiler
def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

@profiler
def round_to_mult(value, multOf):
    return round(value / multOf) * multOf

@profiler
def rand_curve(min: float, max: float, weight: int = 2) -> float:
    total = 0
    for _ in range(weight):
        total += rand.uniform(min, max)
    return total / weight

@profiler
def check_point_rect(point: Vector2, minCorner: Vector2, maxCorner: Vector2) -> bool:
    return minCorner <= point <= maxCorner

@profiler
def check_point_circle(point: Vector2, center: Vector2, radius: float) -> bool:
    return (point.x - center.x) ** 2 + (point.y - center.y) ** 2 <= radius ** 2

@profiler
def check_rect_circle(minCorner: Vector2, maxCorner: Vector2, center: Vector2, radius: float) -> bool:
    closest = Vector2(max(minCorner.x, min(center.x, maxCorner.x)), max(minCorner.y, min(center.y, maxCorner.y)))

    dif = center - closest

    return dif.x ** 2 + dif.y ** 2 <= radius ** 2

@functools.cache
def divided_grid_sizes(precision) -> tuple[int]:
    return tuple([4 ** i for i in range(precision + 1)])

@profiler
def grid_border_search(
        sectorPos: Vector2,
        pos: Vector2,
        radius: float,
        precision: int) -> float:
    sectorCorners = [
        [Vector2(0, 0), False],
        [Vector2(config.SECTOR_SIZE.x, 0), False],
        [Vector2(0, config.SECTOR_SIZE.y), False],
        [Vector2(config.SECTOR_SIZE.x, config.SECTOR_SIZE.y), False]
    ]
    offset = pos - sectorPos * config.SECTOR_SIZE
    offset.x = round_to_mult(offset.x, 1 / 2 ** precision)
    offset.y = round_to_mult(offset.y, 1 / 2 ** precision)

    sectorCorners = tuple(map(lambda x: (x[0].tuple(), check_point_circle(x[0], offset, radius)), sectorCorners))
    
    return _grid_border_search(sectorCorners, offset.x, offset.y, round_to_mult(radius, 1 / 2 ** precision), divided_grid_sizes(precision))

# Recursive internal function to figure out overlap
@functools.cache
def _grid_border_search(corners: tuple[
    tuple[tuple[float, float], bool],
    tuple[tuple[float, float], bool],
    tuple[tuple[float, float], bool],
    tuple[tuple[float, float], bool]
],
posX: float,
posY: float,
radius: float,
dividedGridSizes: tuple[int],
currentPrecision: int = 0) -> float:
    cornerOverlap = len(list(filter(lambda x: x[1], corners)))
    
    # Check if given section is fully overlapping and return full value if so
    if cornerOverlap == 4:
        return 1.0 / dividedGridSizes[currentPrecision]
    
    pos = Vector2(posX, posY)
    outerCorners = [
        [Vector2(*corners[0][0]), corners[0][1]],
        [Vector2(*corners[1][0]), corners[1][1]],
        [Vector2(*corners[2][0]), corners[2][1]],
        [Vector2(*corners[3][0]), corners[3][1]]
    ]

    # Check if no corners overlap and if circle can't intersect regardless, return 0.0 if so
    if cornerOverlap == 0 and not check_rect_circle(outerCorners[0][0], outerCorners[3][0], pos, radius):
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
    innerCorners = tuple(map(lambda x: (x[0].tuple(), check_point_circle(x[0], pos, radius)), innerCorners))
    
    subgrid = (
        (
            corners[0], innerCorners[0],
            innerCorners[1], innerCorners[2]
        ),
        (
            innerCorners[0], corners[1],
            innerCorners[2], innerCorners[3]
        ),
        (
            innerCorners[1], innerCorners[2],
            corners[2], innerCorners[4]
        ),
        (
            innerCorners[2], innerCorners[3],
            innerCorners[4], corners[3]
        )
    )

    # Pass each sub-section into the next layer down then add all the return values together
    return float(sum(map(lambda x: _grid_border_search(x, posX, posY, radius, dividedGridSizes, currentPrecision + 1), subgrid)))