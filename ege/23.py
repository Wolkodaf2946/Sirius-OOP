def f(x,y):
    if y > x or x==22:
        return 0
    if x==y:
        return 1
    else:
        return f(x-2,y) + f(x-5,y) + f(x//2,y)
print(f(47,11))