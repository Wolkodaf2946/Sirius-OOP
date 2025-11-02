class GameSolverOneHeap:
    def __init__(self, operation1, operation2, operation3, winQuantity):
        if "+" in str(operation1) or "-" in str(operation1):
            self.Operation1=str(operation1)
            if "+" in str(operation1):
                self.IsMore = True
            elif "-" in str(operation1):
                self.IsMore = False
            else:
                raise ValueError("Invalid sign")
        else:
            raise ValueError("Invalid sign: operation 1")

        if ("+" in str(operation2) and self.IsMore) or ("-" in str(operation2) and not self.IsMore):
            self.Operation2=str(operation2)
        else:
            raise ValueError("Invalid sign: operation 2")

        if ("*" in str(operation3) and self.IsMore) or ("//" in str(operation3) and not self.IsMore):
            self.Operation3=str(operation3)
        else:
            raise ValueError("Invalid sign: operation 3")

        self.WinQuantity=int(winQuantity)

        if self.IsMore:
            self.Quantity=self.WinQuantity-1
        else:
            self.Quantity=self.WinQuantity+1
        

    def Solve19(self):
        if self.IsMore:
            for s in range(1, self.Quantity+1):
                if self.__solve_task(s, 2):
                    return s
        else:
            for s in range(self.Quantity, 1000):
                if self.__solve_task(s, 2):
                    return s

    def Solve20(self):
        if self.IsMore:
            return [s for s in range (1, self.Quantity+1) if not self.__solve_task(s,1) and self.__solve_task(s,3)]
        else:
            return [s for s in range (self.Quantity, 1000) if not self.__solve_task(s,1) and self.__solve_task(s,3)]

    def Solve21(self):
        if self.IsMore:
            first = set([s for s in range(1,self.Quantity+1) if self.__solve_task(s,2) or self.__solve_task(s,4)])
            second = set([s for s in range(1,self.Quantity+1) if self.__solve_task(s,2)])
            return list(first ^ second)
        else:
            first = set([s for s in range(self.Quantity, 1000) if self.__solve_task(s,2) or self.__solve_task(s,4)])
            second = set([s for s in range(self.Quantity, 1000) if self.__solve_task(s,2)])
            return list(first ^ second)

    def __solve_task(self, stoneQuantity, motion):
        if self.IsMore:
            if stoneQuantity >= self.WinQuantity: return motion % 2 == 0
        else:
            if stoneQuantity <= self.WinQuantity: return motion % 2 == 0  
        if motion == 0: return 0  
        lst = [
            self.__solve_task(eval(str(stoneQuantity)+self.Operation1), motion-1), 
            self.__solve_task(eval(str(stoneQuantity)+self.Operation2), motion-1), 
            self.__solve_task(eval(str(stoneQuantity)+self.Operation3), motion-1),
            ]
        return any(lst) if (motion-1) % 2 == 0 else all(lst)


# solver = GameSolverOneHeap("-3","-5","//4", 30)
# print(solver.Solve19())
# print(*solver.Solve20())
# print(*solver.Solve21())
# print("----------------")
# solver1 = GameSolverOneHeap("+1","+4","*2",51)
# print(solver1.Solve19())
# print(*solver1.Solve20())
# print(*solver1.Solve21())