print("x y z w")
for x in range(2):
    for y in range(2):
        for z in range(2):
            for w in range(2):
                v = z or (x == (y<=w))
                if not(v):
                    print(x,y,z,w)