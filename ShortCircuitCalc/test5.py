import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons


class MyWindow(QMainWindow):
    def __init__(self, rows, cols):
        super().__init__()

        self.figure, self.ax = plt.subplots(rows, cols, figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)

        self.setGeometry(100, 100, 800, 600)
        self.setCentralWidget(self.canvas)

        self.checks = []
        for i in range(rows):
            for j in range(cols):
                ax = self.ax[i, j]
                check = CheckButtons(ax, ['option1', 'option2'], [True, False])
                check.on_clicked(self.on_checked)
                self.checks.append(check)

    def on_checked(self, label):
        for check in self.checks:
            index = check.labels.index(label)
            status = check.get_status()[index]
            print(f'{label} is {status}')
            if label == 'option1':
                print('You selected option 1')
            elif label == 'option2':
                print('You selected option 2')
        print(f'{label} is checked')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow(5, 3)
    window.show()
    sys.exit(app.exec_())