class Shape:
    def __init__(self, *coordinates, color="black", width=2):
        self.color = color
        self.width = width

class Point(Shape):
    def __init__(self, x, y, color="red", width=3):
        super().__init__(x, y, color=color, width=width)
        self.x = x
        self.y = y

    def draw(self, canvas):
        canvas.create_oval(
            self.x - self.width, self.y - self.width,
            self.x + self.width, self.y + self.width,
            fill="blue", outline="black"
        )


class Line(Shape):

    def __init__(self, x1, y1, x2, y2, color="blue", width=2):
        super().__init__(x1, y1, x2, y2, color=color, width=width)
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2

    def draw(self, canvas):
        canvas.create_line(
            self.x1, self.y1, self.x2, self.y2,
            width=self.width, fill=self.color
        )

class Triangle(Shape):
    def __init__(self, x1, y1, x2, y2, x3, y3, color="green", width=2):
        super().__init__(x1, y1, x2, y2, x3, y3, color=color, width=width)
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.x3, self.y3 = x3, y3

    def draw(self, canvas):
        points = [self.x1, self.y1, self.x2, self.y2, self.x3, self.y3]
        canvas.create_polygon(
            points,
            outline=self.color,
            width=self.width
        )


