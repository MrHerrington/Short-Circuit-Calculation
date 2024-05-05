from collections import namedtuple

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import CheckButtons
from ShortCircuitCalc.gui.windows import CustomGraphicView, MainWindow

from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets


class Window(CustomGraphicView):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        ncols = 2
        nrows = 3

        self.canvas = FigureCanvas(Figure(figsize=(ncols * 5, nrows * 3)))

        t = np.arange(0.0, 2.0, 0.01)
        s0 = np.sin(2 * np.pi * t)
        s1 = np.sin(4 * np.pi * t)
        s2 = np.sin(6 * np.pi * t)

        self.ax = self.canvas.figure.subplots(ncols=ncols, nrows=nrows)
        self.checks = dict()
        for row in range(nrows):
            for col in range(ncols):
                ax = self.ax[row, col]
                rax = self.canvas.figure.add_axes([ax.get_position().x0, ax.get_position().y0,
                                                   ax.get_position().width / 2, ax.get_position().height / 2],
                                                  frameon=False)
                rax.set_alpha(0.1)
                # rax = ax.inset_axes([0.05, 0.4, 0.1, 0.15])
                (l0,) = ax.plot(t, s0, visible=False, lw=2, color="k", label="2 Hz")
                (l1,) = ax.plot(t, s1, lw=2, color="r", label="4 Hz")
                (l2,) = ax.plot(t, s2, lw=2, color="g", label="6 Hz")
                lines = [l0, l1, l2]
                labels = [str(line.get_label()) for line in lines]
                visibility = [line.get_visible() for line in lines]
                check = CheckButtons(rax, labels, visibility)
                check.on_clicked(lambda label, i=row, j=col: self.is_click(label, i, j))
                DictButton = namedtuple("DictButton", ["check", "lines", "labels", "visibility"])
                self.checks[row, col] = DictButton(check, lines, labels, visibility)

    def is_click(self, label, i, j):
        index = self.checks[i, j].labels.index(label)
        self.checks[i, j].lines[index].set_visible(
            not self.checks[i, j].lines[index].get_visible()
        )
        self.canvas.draw()
        print('Button is pressed')


def main():
    import sys

    app = QApplication(sys.argv)

    w = MainWindow()
    r = Window()
    w.resultView.scene = QtWidgets.QGraphicsScene()
    w.resultView.scene.addWidget(r.canvas)
    w.resultView.setScene(w.resultView.scene)
    w.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
