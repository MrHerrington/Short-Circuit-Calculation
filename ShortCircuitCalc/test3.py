from PyQt5.QtWidgets import QApplication

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import CheckButtons
from ShortCircuitCalc.gui.windows import CustomGraphicView, MainWindow

from PyQt5 import QtWidgets


class Window(CustomGraphicView):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        ncols = 5
        nrows = 8

        self.canvas = FigureCanvas(Figure(figsize=(ncols * 5, nrows * 3)))

        t = np.arange(0.0, 2.0, 0.01)
        s0 = np.sin(2 * np.pi * t)
        s1 = np.sin(4 * np.pi * t)
        s2 = np.sin(6 * np.pi * t)

        ax = self.canvas.figure.subplots(ncols=ncols, nrows=nrows)
        for col in range(ncols):
            for row in range(nrows):
                (l0,) = ax[row, col].plot(t, s0, visible=False, lw=2, color="k", label="2 Hz")
                (l1,) = ax[row, col].plot(t, s1, lw=2, color="r", label="4 Hz")
                (l2,) = ax[row, col].plot(t, s2, lw=2, color="g", label="6 Hz")
                lines = [l0, l1, l2]
                rax = ax[row, col].inset_axes([0.05, 0.4, 0.1, 0.15])
                labels = [str(line.get_label()) for line in lines]
                visibility = [line.get_visible() for line in lines]
                self.check = CheckButtons(rax, labels, visibility)
                self.check.on_clicked(self.is_click)

        self.canvas.figure.subplots_adjust(left=0.2)

    def is_click(self, label):
        # index = self.labels.index(label)
        # self.lines[index].set_visible(not self.lines[index].get_visible())
        # self.canvas.draw()
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
