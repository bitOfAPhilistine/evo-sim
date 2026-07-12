from tkinter import Canvas, Tk, ttk, TclError
from internal.color import Color
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

monitoring = None
def clear_monitoring():
    global monitoring
    if monitoring != None:
        print(monitoring)
        monitoring = None

def initialize():
    print("Initializing world...")
    global world
    world = World()

    clear_monitoring()

    # Add randomly placed plants
    for _ in range(rand.randint(10, 25)):
        Plant(
            world=world,
            pos=Vector2(rand.uniform(0, config.CANVAS_SIZE.x), rand.uniform(0, config.CANVAS_SIZE.y))
        )

running = True
def on_closing(event=None):
    clear_monitoring()
    print("Closing window")
    global running
    running = False
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)


# On left click, check for an object at the clicked position and print its details
def on_left_click(event):
    clear_monitoring()

    sectors = world.sectors.get_sectors_around(Vector2(event.x // config.SECTOR_SIZE.x, event.y // config.SECTOR_SIZE.y))
    for sector in sectors:
        for obj in sector.objects:
            if obj and (obj.pos - Vector2(event.x, event.y)).magnitude() <= obj.radius:
                print(f"Clicked on: {obj}")
                return
    
    print(f"Clicked on: {world.sectors.get(Vector2(event.x // config.SECTOR_SIZE.x, event.y // config.SECTOR_SIZE.y))}")
canvas.bind("<Button-1>", on_left_click)


# On right click, mark an object to be monitored
def on_right_click(event):
    global monitoring
    clear_monitoring()
    sectors = world.sectors.get_sectors_around(Vector2(event.x // config.SECTOR_SIZE.x, event.y // config.SECTOR_SIZE.y))

    for sector in sectors:
        for obj in sector.objects:
            if obj and (obj.pos - Vector2(event.x, event.y)).magnitude() <= obj.radius:
                monitoring = obj

                print(f"Now monitoring:")
                return
    
    monitoring = world.sectors.get(Vector2(event.x // config.SECTOR_SIZE.x, event.y // config.SECTOR_SIZE.y))
    print(f"Now monitoring:")
canvas.bind("<Button-3>", on_right_click)


# On r, reinitialize the world
def on_r(event):
    print("Manual restart, resetting world...")
    initialize()
root.bind("<r>", on_r)


def main(dt):
    if len(world.objects) == 0:
        print("Mass extinction event, resetting world...")
        initialize()

    world.sectors.update(dt)
    
    for obj in world.updateable:
        if obj:
            try:
                obj.update(dt, canvas)
            except Exception as e:
                print(f"Error updating object {obj}\n{e}")
                obj.delete(canvas)
    
    world.sectors.draw(canvas)

    for obj in world.objects:
        if obj != None:
            try:
                obj.draw(canvas)
            except Exception as e:
                print(f"Error drawing object {obj}\n{e}")
                obj.delete(canvas)
    
    if monitoring != None:
        s = str(monitoring)
        print(s)
        for _ in s.split('\n'):
            print(config.LINE_UP, end=config.LINE_CLEAR)


if __name__ == "__main__":
    dt = 1/60
    initialize()
    while running:
        t = time.time()

        main(dt)

        try:
            root.update()
        except TclError:
            break

        ft = time.time() - t
        time.sleep(max(0, 1/60 - ft))
        dt = max(1/60, ft)