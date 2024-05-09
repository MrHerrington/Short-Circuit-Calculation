import sys

from PyQt5 import QtWidgets, QtCore, QtGui

from ShortCircuitCalc.gui import *
from ShortCircuitCalc.config import *
from ShortCircuitCalc.tools import *


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()
