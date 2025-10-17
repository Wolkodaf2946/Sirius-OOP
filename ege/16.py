from sys import setrecursionlimit

def f(n):
    return g(n+1)

def g(n):
    if n>=30000:
        return 3
    else:
        return g(n+3)+7

setrecursionlimit(10000)
print(f(1500))