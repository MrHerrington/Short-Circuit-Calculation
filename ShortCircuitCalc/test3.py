import sys
from collections import namedtuple

import numpy as np
from matplotlib import figure
from matplotlib.widgets import CheckButtons
from PyQt5 import QtWidgets

from ShortCircuitCalc.gui.windows import MainWindow

ncols = 2
nrows = 3

t = np.arange(0.0, 2.0, 0.01)
s0 = np.sin(2 * np.pi * t)
s1 = np.sin(4 * np.pi * t)
s2 = np.sin(6 * np.pi * t)

fig = figure.Figure(figsize=(ncols * 3, nrows * 2))
ax = fig.canvas.figure.subplots(nrows, ncols)
checks = dict()
for row in range(nrows):
    for col in range(ncols):
        axx = ax[row, col]
        rax = fig.add_axes([axx.get_position().x0, axx.get_position().y0,
                            axx.get_position().width / 2, axx.get_position().height / 2],
                           frameon=False)
        (l0,) = axx.plot(t, s0, visible=False, lw=2, color="k", label="2 Hz")
        (l1,) = axx.plot(t, s1, lw=2, color="r", label="4 Hz")
        (l2,) = axx.plot(t, s2, lw=2, color="g", label="6 Hz")
        lines = [l0, l1, l2]
        labels = [str(line.get_label()) for line in lines]
        visibility = [line.get_visible() for line in lines]
        check = CheckButtons(rax, labels, visibility)
        check.on_clicked(lambda label, i=row, j=col: callback(label, i, j))
        DictButton = namedtuple("DictButton", ["check", "lines", "labels", "visibility"])
        checks[row, col] = DictButton(check, lines, labels, visibility)


def callback(label, i, j):
    index = checks[i, j].labels.index(label)
    checks[i, j].lines[index].set_visible(
        not checks[i, j].lines[index].get_visible()
    )
    fig.canvas.draw()


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.resultView.set_figure(fig)
w.show()
app.exec_()
