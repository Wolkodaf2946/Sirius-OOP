from itertools import *

def u(w,x,y,z): return \
  (w==z) or (not(y<=w)) or (not x)

for a,b,c,d,e in product([0,1],repeat=5):
  t = ((a,0,1,0,0),
       (b,1,1,c,0),
       (0,d,e,0,0))
  if len(t)==len(set(t)):
    for p in permutations('wxyz'):
      if all(u(**dict(zip(p,r)))==r[-1]
             for r in t):
        print(*p)
