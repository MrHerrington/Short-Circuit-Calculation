import sys

from PyQt5 import QtWidgets

from ShortCircuitCalc.tools import *


if __name__ == '__main__':
    chain1 = ElemChain(
        (
            T(160, 'У/Ун-0'),
            QS(160),
            QF(160),
            Line(),
            QF(25),
            W('ВВГ', 3, 4, 20),
            Line(),
            Arc()
        )
    )

    chain2 = ElemChain(
        {
            'TCH': T(160, 'У/Ун-0'),
            'QF1': QF(160),
            'R1': Line(),
            'QF2': QF(25),
            'W1': W('ВВГ', 3, 4, 20)
        }
    )

    chain3 = ("T(160, 'У/Ун-0'), QS(160), QF(160), Line(), QF(25), W('ВВГ', 3, 4, 20), Line(), Arc();"
              "TCH: T(160, 'У/Ун-0'), QF3: QF(100), R1: Line(), QF2: QF(25), W1: W('ВВГ', 3, 4, 20)")

    cs = ChainsSystem(
        chain3
    )

    from ShortCircuitCalc.gui import *
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resultsView.set_figure(GetFigure(cs))
    w.show()
    app.exec_()
