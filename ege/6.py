import turtle as t

k=10
t.left(90)
t.tracer(0)

for i in range(5):
    t.forward(42*k)
    t.right(270)
    t.forward(55*k)
    t.left(90)

t.up()

t.forward(17*k)
t.right(90)
t.forward(12*k)
t.left(90)

t.down()

for i in range(14):
    t.forward(14*k)
    t.left(90)
    t.forward(200*k)
    t.left(90)

t.up()

for x in range(-100,100):
    for y in range(-100,100):
        t.goto(x*k,y*k)
        t.dot(3,"red")
t.done()
