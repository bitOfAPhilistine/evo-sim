from tkinter import Canvas, Tk, ttk, TclError
from internal.plants import Plant
from internal.sectors import Sectors
from internal.smartList import SmartList
from internal.vector2 import Vector2
from internal.objects import GameObject, PhysicsObject

import random as rand
import time
import config


# Initialize the main window
root = Tk()
root.title("Evo-Sim")
root.geometry(f"{config.CANVAS_SIZE.x}x{config.CANVAS_SIZE.y}")

# Create the canvas, offset to the center of the world
frame = ttk.Frame(root, width=config.CANVAS_SIZE.x, height=config.CANVAS_SIZE.y)
canvas = Canvas(frame, width=config.CANVAS_SIZE.x, height=config.CANVAS_SIZE.y, bg="black", offset="center")
frame.pack()
canvas.pack()


class W():
    def __init__(self):
        print("Initializing world...")

        self.objects: SmartList = SmartList()
        self.physObjects: SmartList = SmartList()   
        self.sectors: Sectors = Sectors(1)
        self.plants: SmartList = SmartList()

        # Add randomly placed/sized rocks
        for _ in range(rand.randint(10, 25)):
            GameObject(
                sectors=self.sectors,
                objects=self.objects,
                pos=Vector2(rand.uniform(0, config.CANVAS_SIZE.x), rand.uniform(0, config.CANVAS_SIZE.y)),
                radius=rand.uniform(5, 15),
                color="gray"
            )
        
        # Add randomly placed plants
        for _ in range(rand.randint(10, 25)):
            Plant(
                sectors=self.sectors,
                objects=self.objects,
                plants=self.plants,
                pos=Vector2(rand.uniform(0, config.CANVAS_SIZE.x), rand.uniform(0, config.CANVAS_SIZE.y))
            )
world = W()


# Create a basic object on left mouse click/drag and a physics object on right mouse click/drag, then delete all with spacebar
def on_left_click(event):
    obj = GameObject(
        sectors=world.sectors,
        objects=world.objects,
        pos=Vector2(event.x, event.y),
        radius=10,
        color="white"
    )
canvas.bind("<Button-1>", on_left_click)
canvas.bind("<B1-Motion>", on_left_click)

def on_right_click(event):
    obj = PhysicsObject(
        sectors=world.sectors,
        objects=world.objects,
        physObjects=world.physObjects,
        pos=Vector2(event.x, event.y),
        radius=10,
        color="red",
        mass=1.0,
        drag=0.1
    )
canvas.bind("<Button-3>", on_right_click)
canvas.bind("<B3-Motion>", on_right_click)

def on_spacebar(event=None):
    print("Deleting all objects")
    
    for obj in world.objects:
        if obj != None:
            obj.delete(canvas)
root.bind("<space>", on_spacebar)

running = True
def on_closing(event=None):
    print("Closing window")
    global running
    running = False
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)


def main(dt):
    world.sectors.update(dt)
    
    for obj in world.physObjects:
        if obj:
            obj.update(dt, canvas)
    for obj in world.plants:
        if obj:
            obj.update(dt, canvas)
    
    world.sectors.draw(canvas)

    for obj in world.objects:
        if obj != None:
            obj.draw(canvas)


if __name__ == "__main__":
    dt = 1/60
    while running:
        t = time.time()

        main(dt)

        try:
            root.update()
        except TclError:
            break

        ft = time.time() - t
        print(f"Frame time: {ft:.4f}, Objects: {len(world.objects)}, PhysObjects: {len(world.physObjects)}, Lagging: {ft > 1/60}")
        time.sleep(max(0, 1/60 - ft))
        dt = max(1/60, ft)