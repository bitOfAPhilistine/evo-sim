from tkinter import Canvas
from internal.vector2 import Vector2
from internal.smartList import SmartList
from internal.sectors import Sectors


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
        if self.shape is not None:
            self.canvas.delete(self.shape)
        if self.sectorIndex is not None:
            self.sectors.remove_from_sector(self.sectorPos, self.sectorIndex)
        if self.objectIndex is not None:
            self.objects.remove(self.objectIndex)