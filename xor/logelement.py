class TLogElement:
    def __init__(self):
        self.__in1 = False
        self.__in2 = False
        self._res = False
        self.__nextEl = None
        self.__nextIn = 0

        if not hasattr(self, "calc"):
            raise NotImplementedError("Нельзя создать такой объект")

    def __setIn1 (self, newIn1):
        self.__in1 = newIn1
        self.calc()
        if self.__nextEl:
            if self.__nextIn == 1:
                self.__nextEl.In1 = self._res
            elif self.__nextIn == 2:
                self.__nextEl.In2 = self._res

    def __setIn2 (self, newIn2):
        self.__in2 = newIn2
        self.calc()
        if self.__nextEl:
            if self.__nextIn == 1:
                self.__nextEl.In1 = self._res
            elif self.__nextIn == 2:
                self.__nextEl.In2 = self._res

    def link(self, nextEl, nextIn):
        self.__nextEl = nextEl
        self.__nextIn = nextIn

    In1 = property (lambda x: x.__in1, __setIn1)
    In2 = property (lambda x: x.__in2, __setIn2)
    Res = property (lambda x: x._res)

    def calc (self):
        pass

class TNot (TLogElement):
    def __init__ (self):
        TLogElement.__init__(self)
    def calc(self):
        self._res = not self.In1

class TLog2In(TLogElement):
    pass

class TAnd(TLog2In):
    def __init__(self):
        TLog2In.__init__(self)
    def calc (self):
        self._res = self.In1 and self.In2

class TOr (TLog2In):
    def __init__(self):
        TLog2In.__init__(self)
    def calc(self):
        self._res = self.In1 or self.In2


class TXor (TLog2In):
    def __init__(self):
        TLog2In.__init__(self)
        self.__not1 = TNot()
        self.__not2 = TNot()
        self.__or1 = TOr()
        self.__or2 = TOr()
        self.__and1 = TAnd()

    def calc(self):
        self.__or1.__in1 = self.__in1
        self.__or1.__in2 = self.__in2

        self.__not1.__in1 = self.__in1
        self.__not2.__in1 = self.__in2

        self.__or2.__in1 = self.__not1.Res
        self.__or2.__in2 = self.__not2.Res

        self.__and1.__in1 = self.__or1.Res
        self.__and1.__in2 = self.__or2.Res

        self._res = self.__and1.Res
