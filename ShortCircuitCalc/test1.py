import sys
import pandas as pd

from PyQt5 import QtWidgets
import matplotlib.pyplot as plt
from ShortCircuitCalc.tools import *
from ShortCircuitCalc.gui import *
from ShortCircuitCalc.config import GUI_DIR


dct = {
    T: GUI_DIR / f'{T.__name__}.jpg',
    QF: GUI_DIR / 'QF.jpg',
    QS: GUI_DIR / 'QS.jpg',
    W: GUI_DIR / 'W.jpg',
    Line: GUI_DIR / 'Line.jpg',
    Arc: GUI_DIR / 'Arc.jpg',
}

chain1 = [
    T(160, 'У/Ун-0'),
    QS(160),
    QF(160),
    Line(),
    QF(25),
    W('ВВГ', 3, 4, 20),
    Line(),
    Arc()
]

chain2 = [
    T(250, 'Д/Ун-11'),
    QF(100),
    Line(),
    QF(16),
    W('ВВГ', 3, 2.5, 25),
]

chain3 = [
    T(160, 'У/Ун-0'),
    QS(160),
    QF(160),
    Line(),
    QF(25),
    W('ВВГ', 3, 4, 20),
    Line(),
    Arc()
]

chain4 = [
    T(160, 'У/Ун-0'),
    QS(160),
    QF(160),
    Line(),
    QF(25),
    W('ВВГ', 3, 4, 20),
    Line(),
    Arc(),
]

chain5 = [
    T(250, 'Д/Ун-11'),
    QF(100),
    Line(),
    QF(16),
    W('ВВГ', 3, 2.5, 25),
]

nrows = max(len(chain1), len(chain2), len(chain3), len(chain4), len(chain5))
ncols = len((chain1, chain2, chain3, chain4, chain5))
schem = (chain1, chain2, chain3, chain4, chain5)

fig, ax = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 1))
# fig, ax = plt.subplots(nrows, ncols, figsize=(25, 8))

for idx, col in enumerate(schem):
    for col_pos in range(len(col)):
        axx = ax[col_pos][idx].inset_axes([0, 0, 0.2, 1], anchor='SW')
        axx.axis('off')
        img = plt.imread(dct[col[col_pos].__class__])
        axx.imshow(img, extent=[0, 1, 0, 1])

        resistance_df = pd.DataFrame.from_dict({
            'r1': [col[col_pos].resistance_r1],
            'x1': [col[col_pos].reactance_x1],
            'r0': [col[col_pos].resistance_r0],
            'x0': [col[col_pos].reactance_x0]
        })

        resistance_table = ax[col_pos][idx].table(
            cellText=resistance_df.values, colLabels=resistance_df.columns,
            loc='center', cellLoc='center', bbox=[0.2, 0.5, 0.8, 0.5], fontsize='small',
            colColours=('#9999FF',) * len(resistance_df.columns),
            cellColours=(('#CCCCFF',) * len(resistance_df.columns),) * len(resistance_df.index))

# Turn off axis
for idx, col in enumerate(schem):
    for col_pos in range(max(map(len, schem))):
        ax[col_pos][idx].axis('off')

plt.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.resultView.set_model(fig)
w.show()
app.exec_()
