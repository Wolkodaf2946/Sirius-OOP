import tkinter_figure as tk
from tkinter_figure import figure

root = tk.Tk()
canvas = tk.Canvas(root, width=1080, height=1440, bg="white")
canvas.pack()



line = figure.Line(140, 100, 920, 100)
line.draw(canvas)

triangle = figure.Triangle(1040, 1400, 1000, 1000, 680, 680)
triangle.draw(canvas)

root.mainloop()