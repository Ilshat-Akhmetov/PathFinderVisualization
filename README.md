# Shortest path finding visualization

This projects implements various method to find a shorted path from one point in a grid to another. 
It was developed using PyQT6 framework for GUI applications and python  version 3.8.7.

In this program one can set sell values as non-negative floats/ints or bc.
Here bc stands for blocked cell. It means that a path cannot go through a bc cell.

Current implementation supports four ways to find the shortest path: dfs, bfs, dijkstra and A-star
and can work properly with any grid with size up to 15x15 cells.

In the future I have plans to modify the current implementation, adding possibility to load
grid from a file and making grid and main window more adjustable and convenient for a user.

## How to use it?

Just make sure you have a proper version of PyQT6 from *requirements.txt* and execute:
```
python3 main.py
```

You will get the window where you have to input cell values. Each cell value
means the cost a path should pay to go through the cell. If you set cell value as bc 
then the cell will be unpassable. 

The button *Create grid* will generate you grid with a number of rows and cols according 
to the input boxes and fill grid with *default value*. 

Note that regardless of 
what you see the program assumes that cell values at start point (bottom left) and end point (top right) are equal to zero.

![a grid created](/images/make_grid.png)

After you set your grid you should select the way you want to use for searching the shortest path from
bottom left to top right cell and press *search path*. You will get this:

![the shortest path had been found](/images/search_path.png)

Then you have to clear the results pressing *Create grid* if you want to find the sortest path
with another method/grid.
