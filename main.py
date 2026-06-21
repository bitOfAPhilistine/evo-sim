from tkinter import Canvas, Tk, ttk
from internal.vector2 import Vector2

CANVAS_SIZE = Vector2(1200, 675)

# Initialize the main window
root = Tk()
root.title("Evo-Sim")
root.geometry(f"{CANVAS_SIZE.x}x{CANVAS_SIZE.y}")

# Create the canvas
frame = ttk.Frame(root)
canvas = Canvas(frame, width=CANVAS_SIZE.x, height=CANVAS_SIZE.y, bg="black")

if __name__ == "__main__":
    frame.pack()
    canvas.pack()
    root.mainloop()