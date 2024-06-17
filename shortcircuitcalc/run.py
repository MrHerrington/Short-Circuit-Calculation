# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets
from shortcircuitcalc.gui import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
