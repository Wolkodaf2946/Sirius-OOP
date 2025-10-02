import logelement

elNot = logelement.TNot()
elAnd = logelement.TAnd()
elXor = logelement.TXor()

elAnd.link(elNot, 1)

print("  A | B | not(A&B) ")
print("-------------------")

for A in range(2):
    elAnd.In1 = bool(A)
    for B in range(2):
        elAnd.In2 = bool(B)
        print(" ", A, "|", B, "|", int(elNot.Res))

print("\n")
print("  A | B | A xor B ")
print("-------------------")


for A in range(2):
    elXor.In1 = bool(A)
    for B in range(2):
        elXor.In2 = bool(B)
        print(" ", A, "|", B, "|", int(elXor.Res))