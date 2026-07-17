from tkinter import Canvas, Tk, ttk, TclError
from internal.color import Color
from internal.plants import Plant
from internal.world import Sectors, World
from internal.smartList import SmartList
from internal.vector2 import Vector2
from internal.objects import GameObject, PhysicsObject
from internal.funcs import check_point_circle

import random as rand
import config, time, sys


# Initialize the main window
root = Tk()
root.title("Evo-Sim")
root.geometry(f"{config.CANVAS_SIZE.x}x{config.CANVAS_SIZE.y}")

# Create the canvas, offset to the center of the world
frame = ttk.Frame(root, width=config.CANVAS_SIZE.x, height=config.CANVAS_SIZE.y)
canvas = Canvas(frame, width=config.CANVAS_SIZE.x, height=config.CANVAS_SIZE.y, bg="black", offset="center")
frame.pack()
canvas.pack()

def clear_monitoring():
    if config.monitoring != None:
        for _ in config.monitoringString.split('\n'):
            print(config.LINE_UP, end=config.LINE_CLEAR)
        config.monitoringString = str(config.monitoring)
        print(config.monitoringString)
        if isinstance(config.monitoring, GameObject):
            config.monitoring.strokeColor.b = 0
        config.monitoring = None

def initialize():
    print("Initializing world...")
    global world
    world = World()

    clear_monitoring()

    # Add randomly placed plants
    for _ in range(config.STARTING_PLANTS):
        Plant(
            world=world,
            pos=Vector2(rand.uniform(0, config.CANVAS_SIZE.x), rand.uniform(0, config.CANVAS_SIZE.y))
        )

def on_closing(event=None):
    clear_monitoring()
    print("Closing window")
    config.running = False
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)


# On left click, check for an object at the clicked position and print its details
def on_left_click(event):
    clear_monitoring()
    sector = world.sectors.get(Vector2(event.x // config.SECTOR_SIZE.x, event.y // config.SECTOR_SIZE.y))

    for obj in sector.objects:
        if obj and check_point_circle(Vector2(event.x, event.y).hash(), obj.pos.hash(), obj.radius):
            print(f"Clicked on: {obj}")
            return
    
    print(f"Clicked on: {sector}")
canvas.bind("<Button-1>", on_left_click)


# On right click, mark an object to be monitored
def on_right_click(event):
    clear_monitoring()
    sector = world.sectors.get(Vector2(event.x // config.SECTOR_SIZE.x, event.y // config.SECTOR_SIZE.y))

    for obj in sector.objects:
        if obj and check_point_circle(Vector2(event.x, event.y).hash(), obj.pos.hash(), obj.radius):
            print(f"Now monitoring:")
            config.monitoring = obj
            config.monitoring.strokeColor.b = 255
            config.monitoringString = str(config.monitoring)
            print(config.monitoringString)
            return
    
    print(f"Now monitoring:")
    config.monitoring = sector
    config.monitoringString = str(config.monitoring)
    print(config.monitoringString)
canvas.bind("<Button-3>", on_right_click)


# On r, reinitialize the world
def on_r(event):
    print("Manual restart, resetting world...")
    initialize()
root.bind("<r>", on_r)


def main(dt, startTime):
    if len(world.objects) == 0:
        print("Mass extinction event, resetting world...")
        initialize()

    world.update(canvas, dt, startTime)
    
    world.sectors.draw(canvas)

    for obj in world.objects:
        if obj != None:
            try:
                obj.draw(canvas)
            except Exception as e:
                print(f"Error drawing obj: {obj}\n{e}")
    
    if config.monitoring != None:
        for _ in config.monitoringString.splitlines():
            print(config.LINE_UP, end=config.LINE_CLEAR)
        config.monitoringString = str(config.monitoring)
        print(config.monitoringString)


if __name__ == "__main__":
    dt = config.TARGET_FRAMERATE
    initialize()
    while config.running:
        t = time.time()

        main(dt, t)

        try:
            root.update()
        except TclError:
            break

        ft = time.time() - t
        time.sleep(max(0, config.TARGET_FRAMERATE - ft))
        dt = max(config.TARGET_FRAMERATE, ft)
    sys.exit(0)