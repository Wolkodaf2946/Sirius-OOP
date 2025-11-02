with open("1.txt", "r") as F:
    s = F.readline()
k=m=0

for i in range(len(s)-1):
    if s[i+1]==s[i]:
        k+=1
        m=max(k,m)
    else:
        k=0
print(m+1)