from math import *

a = [tuple(map(float,s.replace(",", ".").split())) for s in open('27b.txt')]

# кластеризация, вариация DBSCAN
r = []
for p in a:
  r += [[p]]
  for c in r[:-1]:
    if any(dist(p,q)<0.1 for q in c):
      r[-1] += c
      r.remove(c)
      
r.sort(key=len,reverse=1)
print(*map(len,r))

def f(x): return int(abs(x)*10000) # окрулгение

# поиск антицентров
cm = [max((sum(dist(a,b) for a in c),b) for b in c)[1]
      for c in r]
print(f(min(x for x,y in cm)),f(max(y for x,y in cm)))

# поиск Q₁ и Q₂
q1 = dist(cm[0],cm[2])
q2 = max(max(dist(a,b) for a in c) for b,c in zip(cm,r))
print(f(q1),f(q2))

# визуализация
from turtle import *
def s(x,y): return x*10,y*10-100 # система координат
tracer(0);up()

# рисуем искомый отрезок, опционально, визуальный контроль
q2,(a,b) = max(max((dist(a,b),(a,b)) for a in c) for b,c in zip(cm,r))
goto(s(*a)); down(); goto(s(*b)); up()

# рисуем кластеры и аномалии
for c,k in zip(r,('red green blue'+' black'*10).split()):
  for p in c:
    goto(s(*p)); dot(2+(len(c)<30)*7,k)











