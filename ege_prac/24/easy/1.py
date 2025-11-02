with open("1.txt", "r") as F:
    s = F.readline()

maxi = 0
count = 0
for i in s:
    if i == "Y":
        count += 1
        maxi = max(count, maxi)
    else:
        count = 0

print(maxi)

#--------------------------

import re
print(max(map(len,re.findall("Y*", s))))