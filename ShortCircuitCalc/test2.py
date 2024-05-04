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

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))

        t = np.arange(0.0, 2.0, 0.01)
        s0 = np.sin(2 * np.pi * t)
        s1 = np.sin(4 * np.pi * t)
        s2 = np.sin(6 * np.pi * t)

        ax = self.canvas.figure.subplots()
        l0, = ax.plot(t, s0, visible=False, lw=2, color="k", label="2 Hz")
        l1, = ax.plot(t, s1, lw=2, color="r", label="4 Hz")
        l2, = ax.plot(t, s2, lw=2, color="g", label="6 Hz")

        self.canvas.figure.subplots_adjust(left=0.2)

        self.lines = [l0, l1, l2]

        rax = self.canvas.figure.add_axes([0.05, 0.4, 0.1, 0.15])

        self.labels = [str(line.get_label()) for line in self.lines]
        visibility = [line.get_visible() for line in self.lines]

        self.check = CheckButtons(rax, self.labels, visibility)
        self.check.on_clicked(self.is_click)

    def is_click(self, label):
        index = self.labels.index(label)
        self.lines[index].set_visible(not self.lines[index].get_visible())
        self.canvas.draw()


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
