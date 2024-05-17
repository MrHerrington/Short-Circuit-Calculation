import sys

from PyQt5 import QtWidgets, QtCore, QtGui

from ShortCircuitCalc.tools import *


if __name__ == '__main__':
    ch = ChainsSystem(
        ((
                T(160, 'У/Ун-0'),
                QS(160),
                QF(160),
                Line(),
                QF(25),
                W('ВВГ', 3, 4, 20),
                Line(),
                Arc()
            ),)
        )
    from ShortCircuitCalc.gui import *
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resultsView.set_figure(ResultsFigure(ch))
    w.show()
    app.exec_()
