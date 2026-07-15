from tkinter import Canvas
from internal.vector2 import Vector2
from internal.smartList import SmartList
from internal.world import Sector, Sectors, World
from internal.color import Color
from internal.funcs import clamp, check_point_circle

import random, math, config


# Base object with basic properties
class GameObject:
    def __init__(self, world: World, pos: Vector2, radius: float, color: Color, strokeColor: Color = Color(0, 0, 0), strokeWidth: int = 1):
        self.world = world
        self.pos = pos
        self.area: float
        self.radius = radius
        self.color = color
        self.strokeColor = strokeColor
        self.strokeWidth = strokeWidth
        self.shape = None
        self.objectIndex = world.objects.add(self)
        self.sectors = self.world.sectors.get_overlapping(self.pos, self.radius)
        self.sectorIndices = self.world.sectors.add_to_sectors(self, self.sectors)
    
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

        if name == 'radius':
            object.__setattr__(self, 'area', self.radius ** 2 * math.pi)
            try:
                self.update_sectors()
            except:
                pass
        elif name == 'pos':
            try:
                self.update_sectors()
            except:
                pass

    def draw(self, canvas: Canvas):
        if not canvas.winfo_exists():
            return
        if self.shape is not None:
            canvas.delete(self.shape)
        
        self.shape = canvas.create_oval(
            self.pos.x - (self.radius - math.ceil(self.strokeWidth / 2)), self.pos.y - (self.radius - math.ceil(self.strokeWidth / 2)),
            self.pos.x + (self.radius - math.ceil(self.strokeWidth / 2)), self.pos.y + (self.radius - math.ceil(self.strokeWidth / 2)),
            fill=self.color.to_hex(),
            outline=self.strokeColor.to_hex(),
            width=self.strokeWidth
        )
    
    def update_sectors(self):
        newSectors = self.world.sectors.get_overlapping(self.pos, self.radius)
        if newSectors != self.sectors:
            self.world.sectors.remove_from_sectors(self.sectors, self.sectorIndices)
            self.sectors = newSectors
            self.sectorIndices = self.world.sectors.add_to_sectors(self, self.sectors)
    
    def delete(self, canvas: Canvas):
        if self.shape is not None and canvas.winfo_exists():
            canvas.delete(self.shape)
            self.shape = None
        if len(self.sectors) > 0:
            self.world.sectors.remove_from_sectors(self.sectors, self.sectorIndices)
        if self.objectIndex is not None:
            self.world.objects.remove(self.objectIndex)


# Physics object
class PhysicsObject(GameObject):
    def __init__(self, 
                    world: World,
                    pos: Vector2, 
                    radius: float, 
                    color: str | Color,
                    mass: float, 
                    drag: float,
                    strokeColor: str | Color = Color(0, 0, 0),
                    strokeWidth: int = 1
                ):
        super().__init__(world, pos, radius, color, strokeColor, strokeWidth)
        self.mass = mass
        self.drag = drag
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.updateableIndex = world.updateable.add(self)
    
    def delete(self, canvas: Canvas):
        super().delete(canvas)
        if self.updateableIndex is not None:
            self.world.updateable.remove(self.updateableIndex)

    def apply_force(self, force: Vector2):
        self.acceleration += force / self.mass
    
    def check_collide(self, other, givenNormal=None):
        totalRadius = self.radius + other.radius
        if check_point_circle(self.pos.hash(), other.pos.hash(), totalRadius):
            # print(f"Colliding {self} with {other}")
            normal = (self.pos - other.pos).normalize() if givenNormal is None else givenNormal

            if normal == Vector2(0, 0):
                normal = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

            self.apply_force(normal.scale(totalRadius - (self.pos - other.pos).magnitude()).scale(self.mass))

            if isinstance(other, PhysicsObject) and givenNormal is None:
                other.check_collide(self, normal.scale(-1))
    
    def check_bounds(self):
        if self.pos.x < 0 + self.radius or self.pos.x > config.CANVAS_SIZE.x - self.radius:
            self.velocity.x *= -1
            self.pos.x = max(self.radius, min(config.CANVAS_SIZE.x - self.radius, self.pos.x))
        if self.pos.y < 0 + self.radius or self.pos.y > config.CANVAS_SIZE.y - self.radius:
            self.velocity.y *= -1
            self.pos.y = max(self.radius, min(config.CANVAS_SIZE.y - self.radius, self.pos.y))

    def update(self, dt, canvas: Canvas):
        self.apply_force(self.velocity.scale(-1).scale(self.drag))

        sectorsToCheck = self.sectors
        for sector in sectorsToCheck:
            objects = sector.objects
            for obj in objects:
                if obj and obj is not self:
                    self.check_collide(obj)

        self.velocity += self.acceleration
        self.pos += self.velocity.scale(dt)
        self.acceleration = Vector2(0)
        self.check_bounds()