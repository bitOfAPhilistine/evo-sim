from internal.vector2 import Vector2

import random as rand
import config
import copy


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


class Tile:
    def __init__(self, nutrients):
        self.nutrients = nutrients
        self.shape = None

class Tiles:
    def __init__(self, blurLevel: int):
        self.width = config.CANVAS_SIZE.x // config.TILE_SIZE.x
        self.height = config.CANVAS_SIZE.y // config.TILE_SIZE.y
        self.tileSize = config.TILE_SIZE
        self.tiles = [[rand.random() for _ in range(self.width)] for _ in range(self.height)]

        # Blur the tiles
        for _ in range(blurLevel):
            prevTiles = copy.deepcopy(self.tiles)
            for y in range(self.height):
                for x in range(self.width):
                    neighbors = []
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                neighbors.append(prevTiles[ny][nx])
                    if neighbors:
                        self.tiles[y][x] = sum(neighbors) / len(neighbors)
    
    def __repr__(self):
        out = ''''''
        for y in range(self.height):
            out += str(self.tiles[y]) + "\n"
        return out
    
    def get_tile(self, x: int, y: int):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def draw(self, canvas):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.get_tile(x, y)
                if tile is None:
                    continue
                
                # Tile should be colored based on its nutrient level, white/light yellow near 0, black near 1, and brown in between
                rgb = (
                    clamp(int((1 - tile) * 255 * 2.5), 0, 255),
                    clamp(int((1 - tile) * 255 * 1.5), 0, 255),
                    clamp(int((0.9 - tile) * 255), 0, 255)
                )

                canvas.create_rectangle(
                    x * self.tileSize.x,
                    y * self.tileSize.y,
                    (x + 1) * self.tileSize.x,
                    (y + 1) * self.tileSize.y,
                    fill=f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
                )