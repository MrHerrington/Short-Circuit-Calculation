import sys
from PyQt5 import QtWidgets

from ShortCircuitCalc.gui.windows import DatabaseBrowser, MainWindow


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    w2 = DatabaseBrowser()
    w2.show()
    app.exec_()
