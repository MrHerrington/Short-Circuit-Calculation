from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import numpy as np
from ShortCircuitCalc.gui import ViewerWindow
from ShortCircuitCalc.database import *


# figure = Figure()
# axes = figure.gca()
# axes.set_title("My Plot")
# x = np.linspace(1, 10)
# y = np.linspace(1, 10)
# y1 = np.linspace(11, 20)
# axes.plot(x, y, "-k", label="first one")
# axes.plot(x, y1, "-b", label="second one")
# axes.legend()
# axes.grid(True)
#
#
# app = QtWidgets.QApplication(sys.argv)
# w = ViewerWindow(figure)
# w.show()
# app.exec_()

Cable.show_table()
