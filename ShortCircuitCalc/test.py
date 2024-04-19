import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from ShortCircuitCalc.database import *


class ScrollableWindow(QtWidgets.QMainWindow):
    def __init__(self, fig):
        self.qapp = QtWidgets.QApplication([])

        QtWidgets.QMainWindow.__init__(self)
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QtWidgets.QVBoxLayout())
        self.widget.layout().setContentsMargins(0,0,0,0)
        self.widget.layout().setSpacing(0)

        self.fig = fig
        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()
        self.scroll = QtWidgets.QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)

        self.nav = NavigationToolbar(self.canvas, self.widget)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)

        self.show()
        exit(self.qapp.exec_())



import matplotlib.pyplot as plt
import numpy as np
import pandas

from matplotlib.table import Table

def main():
    MY_List=[[1,2,5,56,6,7,7,7,7,5],[3,4,5,5,5,5,5,5,5,8],[4,5,6,6,7,7,4,3,4,2],[4,7,2,3,4,5,6,78,8,9],[3,4,5,5,6,6,6,7,77,7],[1,2,3,3,4,5,6,6,7,7],
         [3,4,4,5,5,5,4,4,4,4],[2,2,4,4,5,5,5,5,5,5],[2,2,3,3,4,4,3,2,3,3],[3,3,3,4,5,5,6,7,8,9],[1,1,2,3,4,5,6,6,7,8],[3,4,5,6,7,8,9,98,7,7]]
    data = pandas.DataFrame(MY_List)

    checkerboard_table(data)
    plt.show()


def checkerboard_table(data, fmt='{:.2f}', bkg_colors=['green', 'white']):
    MY_List=[[1,2,5,56,6,7,7,7,7,5],[3,4,5,5,5,5,5,5,5,8],[4,5,6,6,7,7,4,3,4,2],[4,7,2,3,4,5,6,78,8,9],[3,4,5,5,6,6,6,7,77,7],[1,2,3,3,4,5,6,6,7,7],
         [3,4,4,5,5,5,4,4,4,4],[2,2,4,4,5,5,5,5,5,5],[2,2,3,3,4,4,3,2,3,3],[3,3,3,4,5,5,6,7,8,9],[1,1,2,3,4,5,6,6,7,8],[3,4,5,6,7,8,9,98,7,7]]
    # create a figure and some subplots
    fig, ax = plt.subplots(figsize=(len(MY_List[0])*0.5,len(MY_List)*0.5))

    # pass the figure to the custom window
    ax.set_axis_off()
    tb = Table(ax, bbox=[0,0,1,1])

    nrows, ncols = data.shape
    width, height = 1.0 / ncols, 1.0 / nrows
    print(data)

    # Add cells
    for (i,j), val in np.ndenumerate(data):
        # Index either the first or second item of bkg_colors based on
        # a checker board pattern
        idx = [j % 2, (j + 1) % 2][i % 2]
        color = bkg_colors[idx]
        #print(i,j,val)
        #print(data)

        tb.add_cell(i, j, width, height, text=fmt.format(val),
                loc='center', facecolor=color)

    # Row Labels...
    for i, label in enumerate(data.index):
        tb.add_cell(i, -1, width, height, text=label, loc='right',
                edgecolor='none', facecolor='none')
    # Column Labels...
    for j, label in enumerate(data.columns):
        tb.add_cell(-1, j, width, height/2, text=label, loc='center',
                       edgecolor='none', facecolor='none')
    ax.add_table(tb)
    ScrollableWindow(fig)
    # plt.savefig("hk.png")
    return fig

if __name__ == '__main__':
    main()