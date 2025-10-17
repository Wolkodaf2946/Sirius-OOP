with open("24.txt", "r") as F:
	s = F.readline()

k=0
s = s.split("B")
for i in s:
	if i == 'B':
		k+=1
	if