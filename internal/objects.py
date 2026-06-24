from tkinter import Canvas
from internal.vector2 import Vector2
from internal.smartList import SmartList
from internal.sectors import Sectors

import random, config


# Base object with basic properties
class GameObject:
    def __init__(self, canvas: Canvas, sectors: Sectors, objects: SmartList, pos: Vector2, radius: float, color: str | tuple[int, int, int]):
        self.canvas = canvas
        self.sectors = sectors
        self.objects = objects
        self.sectorPos = None
        self.pos = pos
        self.radius = radius
        if isinstance(color, tuple):
            self.color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        else:
            self.color = color
        self.shape = None
        self.objectIndex = objects.add(self)
        self.sectorIndex = None

        self.update_sector()

    def draw(self):
        if not self.canvas.winfo_exists():
            return
        if self.shape is not None:
            self.canvas.delete(self.shape)
        
        self.shape = self.canvas.create_oval(
            self.pos.x - self.radius, self.pos.y - self.radius,
            self.pos.x + self.radius, self.pos.y + self.radius,
            fill=self.color
        )
    
    def update_sector(self):
        sectorPos = Vector2(
            int(self.pos.x // self.sectors.sectorSize.x),
            int(self.pos.y // self.sectors.sectorSize.y)
        )
        if self.sectorPos is None or self.sectorIndex is None or self.sectorPos != sectorPos:
            if self.sectorPos is not None:
                self.sectors.remove_from_sector(self.sectorPos, self.sectorIndex)
            self.sectorPos = sectorPos
            self.sectorIndex = self.sectors.add_to_sector(self.sectorPos, self)
    
    def delete(self):
        if self.shape is not None and self.canvas.winfo_exists():
            self.canvas.delete(self.shape)
            self.shape = None
        if self.sectorIndex is not None and self.sectorPos is not None:
            self.sectors.remove_from_sector(self.sectorPos, self.sectorIndex)
        if self.objectIndex is not None:
            self.objects.remove(self.objectIndex)


# Physics object
class PhysicsObject(GameObject):
    def __init__(self, 
                    canvas: Canvas, 
                    sectors: Sectors, 
                    objects: SmartList, 
                    physObjects: SmartList, 
                    pos: Vector2, 
                    radius: float, 
                    color: str | tuple[int, int, int], 
                    mass: float, 
                    drag: float
                ):
        super().__init__(canvas, sectors, objects, pos, radius, color)
        self.mass = mass
        self.drag = drag
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.physObjects = physObjects
        self.physObjectsIndex = physObjects.add(self)
    
    def delete(self):
        super().delete()
        if self.physObjectsIndex is not None:
            self.physObjects.remove(self.physObjectsIndex)

    def apply_force(self, force: Vector2):
        self.acceleration += force / self.mass
    
    def collide(self, other, givenNormal=None):
        if self.pos.distance_to(other.pos) < self.radius + other.radius:
            # print(f"Colliding {self} with {other}")
            normal = (self.pos - other.pos).normalize() if givenNormal is None else givenNormal

            if normal == Vector2(0, 0):
                normal = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

            self.apply_force(normal.scale(self.radius + other.radius).scale(self.mass))

            if isinstance(other, PhysicsObject) and givenNormal is None:
                other.collide(self, normal.scale(-1))
    
    def checkBounds(self):
        if self.pos.x < 0 + self.radius or self.pos.x > config.CANVAS_SIZE.x - self.radius:
            self.velocity.x *= -1
            self.pos.x = max(self.radius, min(config.CANVAS_SIZE.x - self.radius, self.pos.x))
        if self.pos.y < 0 + self.radius or self.pos.y > config.CANVAS_SIZE.y - self.radius:
            self.velocity.y *= -1
            self.pos.y = max(self.radius, min(config.CANVAS_SIZE.y - self.radius, self.pos.y))

    def update(self, dt):
        self.apply_force(self.velocity.scale(-1).scale(self.drag))

        sectorsToCheck = self.sectors.get_sectors_around(self.sectorPos)
        for sector in sectorsToCheck:
            for obj in sector:
                if obj and obj is not self:
                    self.collide(obj)

        self.velocity += self.acceleration
        self.pos += self.velocity.scale(dt)
        self.acceleration = Vector2(0, 0)
        self.checkBounds()
        self.update_sector()


