def dv(n): return bin(n)[2:]

def r(n):
    new = dv(n)
    if n % 4 == 0: new += new[-2:]
    else:
        ost = dv(n%4)
        new += ost
    return int(new,2)

for i in range(1000000):
    if r(i)>250:
        print(r(i))
        break