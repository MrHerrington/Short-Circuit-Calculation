"""Module text


For correctly working cairosvg first install and
add in PATH environment bin directory variables:
    - gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe;
    - uniconvertor-2.0rc4-win64_headless.msi"""


import sys
from io import BytesIO

import pandas as pd
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
import cairosvg
from PIL import Image

from ShortCircuitCalc.tools import *
from ShortCircuitCalc.gui import *
from ShortCircuitCalc.config import GUI_DIR


dct = {
    T: GUI_DIR / 'resources' / 'graphs' / 'T_star_three.svg',
    QF: GUI_DIR / 'resources' / 'graphs' / 'QF_three.svg',
    QS: GUI_DIR / 'resources' / 'graphs' / 'QS_three.svg',
    W: GUI_DIR / 'resources' / 'graphs' / 'W_three.svg',
    Line: GUI_DIR / 'resources' / 'graphs' / 'Line_three.svg',
    Arc: GUI_DIR / 'resources' / 'graphs' / 'Arc_three.svg',
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

fig, ax = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 1), dpi=240)

for idx, col in enumerate(schem):
    for col_pos in range(len(col)):
        axx = ax[col_pos][idx].inset_axes([0, 0, 0.2, 1], anchor='SW')
        axx.axis('off')
        img_png = cairosvg.svg2png(url=str(dct[col[col_pos].__class__]))
        img = Image.open(BytesIO(img_png))
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

        short_circuit_df = pd.DataFrame.from_dict({
            'I_k(3)': [Calculator(col[:col_pos + 1]).three_phase_current_short_circuit],
            'I_k(2)': [Calculator(col[:col_pos + 1]).two_phase_voltage_short_circuit],
            'I_k(1)': [Calculator(col[:col_pos + 1]).one_phase_voltage_short_circuit]
        })

        short_circuit_table = ax[col_pos][idx].table(
            cellText=short_circuit_df.values, colLabels=short_circuit_df.columns,
            loc='center', cellLoc='center', bbox=[0.4, 0, 0.6, 0.5], fontsize='large',
            colColours=('#FFCC99',) * len(short_circuit_df.columns),
            cellColours=(('#FFE5CC',) * len(short_circuit_df.columns),) * len(short_circuit_df.index))

# Turn off axis
for idx, col in enumerate(schem):
    for col_pos in range(max(map(len, schem))):
        ax[col_pos][idx].axis('off')

plt.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.resultView.set_figure(fig)
w.show()
app.exec_()
