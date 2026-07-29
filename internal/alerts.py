from internal.profiler import profiler

import tkinter as tk
import time, config


canvas: tk.Canvas = None


class Alert:
    def __init__(self, string: str):
        self.string = string
        self.age = 0.0
        self.text = None


alertList: list[Alert] = []
lastUpdateTime = time.time()

@profiler
def add(string: str):
    alertList.insert(0, Alert(string))
    print(string)

@profiler
def update():
    global lastUpdateTime
    if not canvas:
        return

    dt = time.time() - lastUpdateTime

    for i in range(len(alertList)):
        alert = alertList[i]

        alert.age += dt
        
        if i == len(alertList) - 1 and alert.age >= config.ALERT_LIFETIME:
            alertList.pop()
            canvas.delete(alert.text)
            break

        if not alert.text:
            alert.text = canvas.create_text(
                config.CANVAS_SIZE.x - 10, 10,
                fill=config.TEXT_COLOR,
                anchor="ne",
                text=alert.string
            )

        canvas.coords(
            alert.text,
            (config.CANVAS_SIZE.x - 10, 10 + i * 16)
        )
        canvas.tkraise(alert.text)

    lastUpdateTime = time.time()