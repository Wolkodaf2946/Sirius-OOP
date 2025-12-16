def f(x,y):
    return (2*x*y > A) or (y<x) or (x<15)

for A in range(1000):
    if all(f(x,y) for x in range(1000) for y in range(1000)):
        print(A)