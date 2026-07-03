from tkinter import Canvas, Tk, ttk, TclError
from internal.plants import Plant
from internal.world import Sectors, World
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


world = World()

# Add randomly placed/sized rocks
for _ in range(rand.randint(10, 25)):
    GameObject(
        world=world,
        pos=Vector2(rand.uniform(0, config.CANVAS_SIZE.x), rand.uniform(0, config.CANVAS_SIZE.y)),
        radius=rand.uniform(5, 15),
        color="gray"
    )

# Add randomly placed plants
for _ in range(rand.randint(10, 25)):
    Plant(
        world=world,
        pos=Vector2(rand.uniform(0, config.CANVAS_SIZE.x), rand.uniform(0, config.CANVAS_SIZE.y)),
        maxRadius=rand.uniform(1.0, 50.0),
        growthSpeed=rand.uniform(0.0, 2.0),
        rootDepth=rand.uniform(0.0, 1.0),
        seedSpeed=rand.uniform(0.0, 10.0)
    )

running = True
def on_closing(event=None):
    print("Closing window")
    global running
    running = False
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)


def main(dt):
    world.sectors.update(dt)
    
    for obj in world.updateable:
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
        print(f"Frame time: {ft:.4f}, Objects: {len(world.objects)}, Updateable: {len(world.updateable)}, Lagging: {ft > 1/60}")
        time.sleep(max(0, 1/60 - ft))
        dt = max(1/60, ft)