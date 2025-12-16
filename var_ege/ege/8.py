from itertools import product

cmd = product('БУРАТИНО', repeat=5)
c=0
for i in cmd:
    c = c+1
    s = ''.join(i)
    if c % 2 != 0 and (s[0] not in ['А','И','О']) and (len(s)==len(set(s))):
        print(c)