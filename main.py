from tkinter import Canvas, Tk, ttk
from internal.sectors import Sectors
from internal.smartList import SmartList
from internal.vector2 import Vector2
from internal.objects import GameObject, PhysicsObject

import time
import config


# Initialize the main window
root = Tk()
root.title("Evo-Sim")
root.geometry(f"{config.CANVAS_SIZE.x}x{config.CANVAS_SIZE.y}")

# Create the canvas, offset to the center of the world
frame = ttk.Frame(root, width=config.CANVAS_SIZE.x, height=config.CANVAS_SIZE.y)
canvas = Canvas(frame, width=config.CANVAS_SIZE.x, height=config.CANVAS_SIZE.y, bg="black", offset="center")

# Add an xy gradient background for testing
gradSize = Vector2(config.CANVAS_SIZE.x // 10, config.CANVAS_SIZE.y // 10)
for y in range(gradSize.y):
    for x in range(gradSize.x):
        color = f"#{int(255 * x / gradSize.x):02x}{int(255 * y / gradSize.y):02x}00"
        canvas.create_rectangle(x * 10, y * 10, (x + 1) * 10, (y + 1) * 10, fill=color)

objects = SmartList()
physObjects = SmartList()

sectors = Sectors(config.CANVAS_SIZE.x // config.SECTOR_SIZE.x, config.CANVAS_SIZE.y // config.SECTOR_SIZE.y)

# Create a basic object on left mouse click and a physics object on right mouse click, then delete all with spacebar
def on_left_click(event):
    obj = GameObject(
        canvas=canvas,
        sectors=sectors,
        objects=objects,
        pos=Vector2(event.x, event.y),
        radius=10,
        color="white"
    )
    obj.draw()
canvas.bind("<Button-1>", on_left_click)

def on_right_click(event):
    obj = PhysicsObject(
        canvas=canvas,
        sectors=sectors,
        objects=objects,
        physObjects=physObjects,
        pos=Vector2(event.x, event.y),
        radius=10,
        color="red",
        mass=1.0,
        drag=0.1
    )
    obj.draw()
canvas.bind("<Button-3>", on_right_click)

def on_spacebar(event=None):
    print("Deleting all objects")

    for obj in objects:
        if obj != None:
            obj.delete()
canvas.bind("<space>", on_spacebar)


def main(dt):
    for obj in physObjects:
        if obj:
            obj.update(dt)
    
    for obj in objects:
        if obj != None:
            obj.draw()


if __name__ == "__main__":
    dt = 1/60
    while True:
        t = time.time()

        main(dt)

        frame.pack()
        canvas.pack()
        root.update()

        ft = time.time() - t
        print(f"Frame time: {ft:.4f}, Objects: {len(objects)}, PhysObjects: {len(physObjects)}")
        time.sleep(max(0, 1/60 - ft))
        dt = max(1/60, ft)