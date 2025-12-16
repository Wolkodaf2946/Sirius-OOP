def func(s,p):
    if s >= 444: return p%2==0
    if p==0: return 0

    lst = [func(s+2, p-1), func(s+5,p-1), func(s*3,p-1)]
    return all(lst) if p%2==0 else any(lst)

for s in range(1, 400+1):
    if func(s,2):
        print(s)
        break