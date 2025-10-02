import tkinter as tk
from tkinter_figure import figure

root = tk.Tk()
canvas = tk.Canvas(root, width=1080, height=1440, bg="white")
canvas.pack()

point = figure.Point(540, 1300, width=30)

line = figure.Line(140, 100, 920, 100, width=10)


triangle = figure.Triangle(540, 500, 340, 900, 740, 900, width=10)


slices = [point, line, triangle]

for i in slices:
    i.draw(canvas)

root.mainloop()