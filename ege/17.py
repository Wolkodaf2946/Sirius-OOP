a = [int(a) for a in open("17.txt")]
mini = min([s for s in a if len(str(abs(s)))==3 and s%10==9])
k = []

for i in range(len(a)-1):
    q,w=a[i], a[i+1]
    if len(str(abs(q)))==2 or len(str(abs(w)))==2:
        if (q+w)%mini==0:
            k.append(q+w)
print(len(k), max(k))