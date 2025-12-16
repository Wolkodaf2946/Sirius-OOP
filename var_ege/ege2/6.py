import turtle as t
from math import sin, pi

k = 20

t.right(270)
t.tracer(0)

t.up()
for x in range(-50,50):
    for y in range(-50,50):
        t.goto(x*k,y*k)
        t.dot(5,"red")
t.down()

t.forward(5*k)
t.right(60)

for _ in range(6):
    t.forward(23*k)
    t.right(45)
    t.forward(17*k)
    t.right(135)

t.left(90)
t.forward(7*k)

t.done()
print(23*17*sin(pi/4))