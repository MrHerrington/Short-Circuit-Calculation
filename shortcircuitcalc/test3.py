import sys
from PyQt5 import QtWidgets

from shortcircuitcalc.gui.windows import DatabaseBrowser, MainWindow


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # w = MainWindow()
    w2 = DatabaseBrowser()
    # w.show()
    w2.show()
    app.exec_()
