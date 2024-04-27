import pandas as pd
import matplotlib.pyplot as plt
from ShortCircuitCalc.tools import *
from ShortCircuitCalc.config import GUI_DIR
from ShortCircuitCalc.gui import ViewerWidget, CustomGraphicView
from PyQt5 import QtWidgets
import sys


dct = {
    T: GUI_DIR / 'T.jpg',
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

fig, ax = plt.subplots(nrows, ncols, figsize=(ncols * 3, nrows * 0.8))

for idx, col in enumerate(schem):
    for col_pos in range(len(col)):
        ax[col_pos][idx].set_aspect(2/10)
        axx = ax[col_pos][idx].inset_axes([0, 0, 0.5, 1], anchor='SW')
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
            loc='center', cellLoc='center', bbox=[0.2, 0.5, 0.8, 0.5], fontsize='large',
            colColours=('#9999FF',) * len(resistance_df.columns),
            cellColours=(('#CCCCFF',) * len(resistance_df.columns),) * len(resistance_df.index))

# Turn off axis
for idx, col in enumerate(schem):
    for col_pos in range(max(map(len, schem))):
        ax[col_pos][idx].axis('off')

plt.subplots_adjust(hspace=0)
plt.tight_layout()


app = QtWidgets.QApplication(sys.argv)
w = ViewerWidget(fig)
w.show()
app.exec_()
