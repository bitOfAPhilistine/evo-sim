from tkinter import Canvas, Tk, ttk
from internal.sectors import Sectors
from internal.smartList import SmartList
from internal.vector2 import Vector2
from internal.objects import GameObject

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

sectors = Sectors(config.CANVAS_SIZE.x // config.SECTOR_SIZE.x, config.CANVAS_SIZE.y // config.SECTOR_SIZE.y)

# Create a test object on left mouse click and remove all on right mouse click
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
    
    print(objects)
    print(sectors)
canvas.bind("<Button-1>", on_left_click)

def on_right_click(event):
    for obj in objects:
        if obj != None:
            obj.delete()
    
    print(objects)
    print(sectors)
canvas.bind("<Button-3>", on_right_click)


if __name__ == "__main__":
    frame.pack()
    canvas.pack()
    root.mainloop()