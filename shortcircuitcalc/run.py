# -*- coding: utf-8 -*-
"""
The module running the program.

"""


import os
import sys
sys.path.append(os.getcwd())
from PyQt5 import QtWidgets
from shortcircuitcalc.gui import MainWindow


def main():
    """
    The function creates and shows app main window.

    """
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
