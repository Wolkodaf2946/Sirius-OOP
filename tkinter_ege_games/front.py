from PySide6 import QtWidgets
import MainGui
import sys
import logging
import solver

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')

class App(QtWidgets.QMainWindow, MainGui.Ui_MainWindow):
    def __init__(self):
        self.__isInitOk = False

        super().__init__()
        self.setupUi(self)

        self.initButton_2.clicked.connect(self.__initButtonClicked)
        self.solveButton.clicked.connect(self.__solveButtonClicked)

    def __initButtonClicked(self):
        self.__isInitOk = True

        sign1 = self.operation1.text()
        step1 = self.quantity1.text()
        self.__operation1 = sign1+step1
        logging.debug(f"init operation 1 -> {self.__operation1}")

        sign2 = self.operation2.text()
        step2 = self.quantity2.text()
        self.__operation2 = sign2+step2
        logging.debug(f"init operation 2 -> {self.__operation2}")

        sign3 = self.operation3.text()
        step3 = self.quantity3.text()
        self.__operation3 = sign3+step3
        logging.debug(f"init operation 3 -> {self.__operation3}")

        self.__winQuantity = self.quantityWin.text()
        logging.debug(f"init the winning number of stones in the pile -> {self.__winQuantity}")

        if self.__isInitOk:
            self.__engine = solver.GameSolverOneHeap(
                self.__operation1,
                self.__operation2,
                self.__operation3,
                self.__winQuantity
            )
            self.solveButton.setEnabled(True)
        else:
            self.solveButton.setEnabled(False)

    def __solveButtonClicked(self):
        res19 = self.__engine.Solve19()
        res20 = self.__engine.Solve20()
        res21 = self.__engine.Solve21()

        self.answer19.setText(str(res19))
        self.answer20.setText(str(res20))
        self.answer21.setText(str(res21))

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = App()
    main_window.show()
    app.exec()

if __name__ == "__main__":
    main()

