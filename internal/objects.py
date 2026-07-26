from tkinter import Canvas
from internal.vector2 import Vector2
from internal.smartList import SmartList
from internal.world import Sector, Sectors, World
from internal.color import Color
from internal.funcs import *
from internal.profiler import profiler

import internal.globals as globals
import random, math, config, time, sys, gc


# Base object with basic properties
class GameObject:
    @profiler
    def __init__(self, world: World, pos: Vector2, radius: float, color: Color, strokeColor: Color = Color(0, 0, 0), strokeWidth: int = 1):
        self.world = world
        self.pos = pos
        self.area: float
        self.radius = radius
        self.color = color.copy()
        self.strokeColor = strokeColor.copy()
        self.strokeWidth = strokeWidth
        self.shape = None
        self.objectIndex = world.objects.add(self)
        self.sectors = self.world.sectors.get_overlapping(self.pos, self.radius)
        self.sectorIndices = self.world.sectors.add_to_sectors(self, self.sectors)
        self.beingMonitored = False
        self.redraw = True

        if globals.debug:
            print(f"Created: {object.__repr__(self)}")
    
    @profiler
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

        if name == 'radius':
            object.__setattr__(self, 'area', self.radius ** 2 * math.pi)
        if name in ('radius', 'pos'):
            if self.can_update_sectors():
                self.update_sectors()
        if name in ('radius', 'pos', 'color', 'strokeColor', 'strokeWidth'):
            self.redraw = True
    
    @profiler
    def readout(self):
        return f'''GameObject:
    Position: {self.pos.x:.2f}, {self.pos.y:.2f}
    Color: {self.color}
    Radius: {self.radius:.2f}
    Area: {self.area:.2f}
    Sector Overlaps:
    {'\n    '.join(map(str, zip(map(lambda x: x.sectorPos, self.sectors), self.sectorOverlaps)))}'''

    @profiler
    def draw(self, canvas: Canvas):
        if not self.shape:
            self.shape = canvas.create_oval(
                self.pos.x - self.radius, self.pos.y - self.radius, self.pos.x + self.radius, self.pos.y + self.radius,
                fill=self.color.to_hex(),
                outline=self.strokeColor.to_hex(),
                width=self.strokeWidth
            )
        
        if self.redraw:
            if not canvas.winfo_exists():
                return
            
            canvas.coords(
                self.shape,
                (self.pos.x - self.radius, self.pos.y - self.radius, self.pos.x + self.radius, self.pos.y + self.radius)
            )
            canvas.itemconfig(
                self.shape,
                fill=self.color.to_hex(),
                outline=self.strokeColor.to_hex(),
                width=self.strokeWidth
            )

            self.redraw = False
    
    @profiler
    def update_sectors(self):
        newSectors = self.world.sectors.get_overlapping(self.pos, self.radius)
        if newSectors != self.sectors:
            self.world.sectors.remove_from_sectors(self.sectors, self.sectorIndices)
            self.sectors = newSectors
            self.sectorIndices = self.world.sectors.add_to_sectors(self, self.sectors)
    
    @profiler
    def can_update_sectors(self):
        return hasattr(self, 'pos') and hasattr(self, 'radius') and hasattr(self, 'sectors')
    
    @profiler
    def delete(self, canvas: Canvas):
        if globals.debug:
            print(f"Deleting: {object.__repr__(self)}")
        
        if self.beingMonitored:
            globals.clearMonitoring = True
        
        if self.shape is not None and canvas.winfo_exists():
            canvas.delete(self.shape)
            self.shape = None
        if len(self.sectors) > 0:
            self.world.sectors.remove_from_sectors(self.sectors, self.sectorIndices)
        if self.objectIndex is not None:
            self.world.objects.remove(self.objectIndex)


# Physics object
class PhysicsObject(GameObject):
    @profiler
    def __init__(self, 
                    world: World,
                    pos: Vector2,
                    radius: float,
                    color: str | Color,
                    density: float,
                    drag: float,
                    strokeColor: str | Color = Color(0, 0, 0),
                    strokeWidth: int = 1
                ):
        super().__init__(world, pos, radius, color, strokeColor, strokeWidth)
        self.density = density
        self.drag = drag
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.updateableIndex = world.updateable.add(self)
        self.lastUpdated = time.time()
    
    @profiler
    def readout(self):
        return f'''PhysicsObject:
    Position: {self.pos.x:.2f}, {self.pos.y:.2f}
    Velocity: {self.velocity.x:.2f}, {self.velocity.y:.2f}
    Color: {self.color}
    Radius: {self.radius:.2f}
    Area: {self.area:.2f}
    Density: {self.density:.2f}
    Mass: {self.mass():.2f}
    Sector Overlaps:
    {'\n    '.join(map(str, zip(map(lambda x: x.sectorPos, self.sectors), self.sectorOverlaps)))}'''
    
    @profiler
    def delete(self, canvas: Canvas):
        super().delete(canvas)
        if self.updateableIndex is not None:
            self.world.updateable.remove(self.updateableIndex)

    def apply_force(self, force: Vector2):
        self.acceleration += force / self.mass()

    @profiler
    def mass(self):
        return self.area * self.density
    
    @profiler
    def check_collide(self, other, givenNormal=None):
        totalRadius = self.radius + other.radius
        if check_point_circle(self.pos, other.pos, totalRadius):
            normal = (self.pos - other.pos).normalize() if givenNormal is None else givenNormal

            if normal == Vector2(0, 0):
                normal = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

            self.apply_force(normal.scale(totalRadius - (self.pos - other.pos).magnitude()).scale(self.mass()))

            if isinstance(other, PhysicsObject) and givenNormal is None:
                other.check_collide(self, normal.scale(-1))
    
    @profiler
    def check_bounds(self):
        if self.pos.x < 0 + self.radius or self.pos.x > config.CANVAS_SIZE.x - self.radius:
            self.velocity.x *= -1
            self.pos.x = max(self.radius, min(config.CANVAS_SIZE.x - self.radius, self.pos.x))
        if self.pos.y < 0 + self.radius or self.pos.y > config.CANVAS_SIZE.y - self.radius:
            self.velocity.y *= -1
            self.pos.y = max(self.radius, min(config.CANVAS_SIZE.y - self.radius, self.pos.y))

    @profiler
    def update(self, canvas: Canvas):
        dt = min(config.TARGET_FRAMERATE * 10.0, time.time() - self.lastUpdated)

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

        self.lastUpdated = time.time()