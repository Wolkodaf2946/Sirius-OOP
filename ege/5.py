def sc(n):
	copy = n
	x = ''
	while copy > 0:
		x = str(copy % 3) + x
		copy = copy // 3
	return x


def r(n):
    t = sc(n)
    if n % 5 == 0:
        t = t + t[-2:]
    else:
        ost = sc((n%5)*7)
        t = t + ost
    return int(t, 3)

while True:
    n=30
    if r(n) > 273:
        print(r(n))
        print(n-1)
        break
    n+=1