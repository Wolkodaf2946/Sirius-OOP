from itertools import *

s = 'ADEF BDF CFG DABE EADG FABC GCE'
#d = {c:set(v) for c,*v in s.split()}

z = '123 2145 316 427 5267 6357 7456'

for x in permutations(set(s)-{' '}):
  t = z
  for a,b in zip('1234567',x):
    t = t.replace(a,b)

  #g = {c:set(v) for c,*v in t.split()}
  g = ' '.join(c+''.join(sorted(v)) for c,*v in sorted(t.split()))
  if g==s:
    print(*x,sep='')
