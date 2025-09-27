import math


class Figure:
    def __init__(self, length1, length2, length3):
        self.length1 = length1
        self.length2 = length2
        self.length3 = length3


class Circle(Figure):
    def __init__(self, length):
        super().__init__(length, None, None)

    def GetPerimeter(self):
        return 2*math.pi*self.length1
    def GetSquare(self):
        return math.pi*self.length1**2

class Square(Figure):
    def __init__(self, length):
        super().__init__(length, None, None)

    def GetPerimeter(self):
        return 4*self.length1
    def GetSquare(self):
        return self.length1**2

class Triangle(Figure):
    def __init__(self, length1, length2, length3):
        if (length1+length2)<=length3 or (length2+length3)<=length1 or (length3+length1)<=length2:
            raise ValueError("incorrect value")
        super().__init__(length1, length2, length3)

    def GetPerimeter(self):
        return self.length1 + self.length2 + self.length3
    def GetSquare(self):
        p = self.GetPerimeter()/2
        return math.sqrt(p*(p-self.length1)*(p-self.length2)*(p-self.length3))


circle = Circle(1)
square = Square(1)
triangle = Triangle(1,1,1)
figure = [circle, square, triangle]

for i in figure:
    print(i.GetSquare())