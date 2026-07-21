from internal.color import Color
from internal.plants import Plant
from internal.world import Sector, Sectors, World
from internal.smartList import SmartList
from internal.vector2 import Vector2
from internal.objects import GameObject, PhysicsObject
from internal.funcs import *
from internal.profiler import profiler

import tkinter as tk
import internal.globals as globals
import random as rand
import config, time, sys, gc, getopt


# Initialize the main window
root = tk.Tk()
root.title("Evo-Sim")
root.geometry(f"{config.CANVAS_SIZE.x}x{config.CANVAS_SIZE.y}")

# Create the canvas, offset to the center of the world
frame = tk.Frame(root, width=config.CANVAS_SIZE.x, height=config.CANVAS_SIZE.y)
canvas = tk.Canvas(frame, width=config.CANVAS_SIZE.x, height=config.CANVAS_SIZE.y, offset="center")
frame.pack()
canvas.pack()

# Process arguments
args = sys.argv[1:]
options = "hdp"
longOptions = ["Help", "Debug", "Profiler"]
helpMsg = '''Terminal Args:
-h or --Help: prints this message
-d or --Debug: enable debug printing
-p or --Profiler: enable profiler

In-Sim Controls:
Left-Click: prints stats of the thing clicked on
Right-Click: continuously prints stats of the thing clicked on until something else is selected'''
try:
    args, _ = getopt.getopt(args, options, longOptions)
    for arg, _ in args:
        match arg:
            case '-h' | "--Help":
                globals.running = False
                print(helpMsg)
                sys.exit(0)
            case '-d' | "--Debug":
                globals.debug = True
            case '-p' | "--Profiler":
                globals.profiling = True
except getopt.error as err:
    print(str(err))

@profiler
def clear_monitoring():
    if globals.monitoring:
        canvas.delete(globals.monitoringText)

        globals.monitoring.beingMonitored = False

        if isinstance(globals.monitoring, GameObject):
            globals.monitoring.strokeColor.b = 0
            globals.monitoring.redraw = True
        elif isinstance(globals.monitoring, Sector):
            canvas.itemconfig(globals.monitoring.shape, outline='')
        
        globals.monitoring = None
        globals.monitoringText = None
        globals.clearMonitoring = False

def profilerTimes_to_string(times, parentTotal = 1.0, depth = 0) -> str:
    output: str = ""
    sortedTimes = sorted(times, key=lambda x: times[x].totalTime, reverse=True)
    for func in sortedTimes:
        data = times[func]
        output += f"{"  " * depth}{func.__qualname__}: called {data.callCount} times, total {data.totalTime}s taken, average {data.avgTime}s, max {data.maxTime}{f", percentage of parent time: {data.totalTime / parentTotal * 100.0:.2f}%" if depth > 0 else ''}\n"
        if len(data.children) > 0:
            output += profilerTimes_to_string(data.children, data.totalTime, depth + 1)
    return output

def profiledFrameTimes_to_string(ft) -> str:
    output: str = f"Frame Time: {ft}:\n"
    sortedTimes = sorted(globals.profiledFrameTimes, key=lambda x: globals.profiledFrameTimes[x].totalTime, reverse=True)
    for func in sortedTimes:
        data = globals.profiledFrameTimes[func]
        output += f"{func.__qualname__}: called {data.callCount} times, total {data.totalTime}s taken\n"
    return output


@profiler
def initialize():
    clear_monitoring()
    print("Initializing world...")
    global world
    world = World()

    # Add randomly placed plants
    for _ in range(config.STARTING_PLANTS):
        Plant(
            world=world,
            pos=Vector2(rand.uniform(0, config.CANVAS_SIZE.x), rand.uniform(0, config.CANVAS_SIZE.y))
        )


def on_closing(event=None):
    clear_monitoring()
    print("Closing window")
    globals.running = False
    root.destroy()
    if len(globals.profilerTimes) > 0:
        with open("internal/profiler.txt", 'w') as f:
            s = profilerTimes_to_string(globals.profilerTimes)
            s += "\n\nLag Spikes:" + globals.lagSpikeLog
            f.write(s)
root.protocol("WM_DELETE_WINDOW", on_closing)


# On left click, clear monitored object
@profiler
def on_left_click(event):
    clear_monitoring()
canvas.bind("<Button-1>", on_left_click)


# On right click, mark an object to be monitored
@profiler
def on_right_click(event):
    clear_monitoring()
    sector = world.sectors.get(Vector2(event.x // config.SECTOR_SIZE.x, event.y // config.SECTOR_SIZE.y))

    for obj in sector.objects:
        if obj and check_point_circle(Vector2(event.x, event.y), obj.pos, obj.radius):
            globals.monitoring = obj
            globals.monitoring.beingMonitored = True
            globals.monitoring.strokeColor.b = 255
            globals.monitoring.redraw = True
            return
    
    globals.monitoring = sector
    globals.monitoring.beingMonitored = True
    canvas.itemconfig(globals.monitoring.shape, outline='blue')
canvas.bind("<Button-3>", on_right_click)


# On w, start monitoring the world
@profiler
def on_w(event):
    clear_monitoring()
    globals.monitoring = world
    globals.monitoring.beingMonitored = True
root.bind("<w>", on_w)


# On r, reinitialize the world
@profiler
def on_r(event):
    clear_monitoring()
    print("Manual restart, resetting world...")
    initialize()
root.bind("<r>", on_r)


# On d, toggle debug printing
@profiler
def on_d(event):
    globals.debug = not globals.debug
    print("Debug printing activated" if globals.debug else "Debug printing deactivated")
root.bind("<d>", on_d)


@profiler
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
    
    if globals.clearMonitoring:
        clear_monitoring()
    
    if globals.monitoring:
        if not globals.monitoringText:
            globals.monitoringText = canvas.create_text(
                10, 10,
                fill="light blue",
                anchor="nw"
            )
        
        canvas.itemconfig(globals.monitoringText,
            text=globals.monitoring.readout()
        )
        canvas.tkraise(globals.monitoringText)


if __name__ == "__main__" and globals.running:
    dt = config.TARGET_FRAMERATE
    initialize()
    
    while globals.running:
        t = time.time()

        main(dt, t)

        try:
            root.update()
        except tk.TclError:
            break

        ft = time.time() - t
        if len(globals.profiledFrameTimes) > 0:
            if ft > config.TARGET_FRAMERATE * 5:
                print("Lag spike:")
                s = profiledFrameTimes_to_string(ft)
                print(s)
                globals.lagSpikeLog += '\n\n' + s
            globals.profiledFrameTimes = {}

        time.sleep(max(0, config.TARGET_FRAMERATE - ft))
        dt = max(config.TARGET_FRAMERATE, ft)
    sys.exit(0)