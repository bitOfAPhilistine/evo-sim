# Evolution Sim in Python

## Overview
This is a project I made for the personal project on Boot.dev, I was a bit overambitious and spent longer than I'd like on this but I got it done. The simulation consists of circular plants, in a world split into sectors with different nutrient levels. Originally I was planning to add simple animals as well but I quickly realized that that would be WAY to ambitious for the course project and decided to limit it to only plants.

## Requirements and Usage
 - Python 3
 - Tkinter (should be installed with Python be default)

To run the program, either run the run.sh file, or run the main.py file in the terminal. The program accepts the following args in the terminal:

-h or --Help: prints a message containing all accepted args and in-sim controls

-d or --Debug: enable debug printing

-p or --Profiler: enable profiler

## Controls
Right Click: starts monitoring the thing clicked on

Left Click: clears the monitoring text

W: starts monitoring the world

S: toggles showing the species id of each plant

R: restarts the world

D: toggles debug printing


## Features
 - A species system which creates new species if a mutated plant successfully has offspring, the species id of each plant can be seen by pressing s.
 - The ability to monitor the stats of any plant or sector by right-clicking on them, which will be displayed in the top right, the world as a whole can be monitored with w.
 - A custom event system which temporarily displays text in the top left, mainly whenever a species is created or goes extinct
 - A custom quadtree search algorithm to estimate how much of each plant overlaps with each sector (I did not know what a quadtree search was before I made one). I realized after I implemented this that there were other, more efficient algorithms for doing the same task, but since I was proud of this implementation, and this is a project intended to display my skills, I have elected to keep this algorithm.
 - A custom profiler wrapper which can record the time taken by each function registered and group those function calls by which function called them, all of which is printed to a profiler.txt file. This can be activated by running the main.py file from the terminal with the -p arg