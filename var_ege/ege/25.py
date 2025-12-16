from fnmatch import *

for x in range(0,10**10,2026):
    if fnmatch(str(x), "431*7?14"):
        print(x, x//2026)