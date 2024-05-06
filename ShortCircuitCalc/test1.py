"""Module text


For correctly working cairosvg first install and
add in PATH environment bin directory variables:
    - gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe;
    - uniconvertor-2.0rc4-win64_headless.msi"""

import sys
from io import BytesIO
from itertools import cycle
from collections import namedtuple

import pandas as pd
from matplotlib import figure
from matplotlib.widgets import CheckButtons
from PyQt5 import QtWidgets
import cairosvg
from PIL import Image

from ShortCircuitCalc.tools import *
from ShortCircuitCalc.gui import *

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

fig = figure.Figure(figsize=(ncols * 5, nrows * 1))
ax = fig.canvas.figure.subplots(nrows, ncols)
fig.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)

checks = dict()
for idx, row in enumerate(schem):
    for col in range(len(row)):
        axx = ax[col, idx].inset_axes([0, 0, 0.2, 1], anchor='SW')
        axx.axis('off')

        rax = fig.add_axes([axx.get_position().x0, axx.get_position().y0,
                            axx.get_position().width / 2, axx.get_position().height / 2],
                           frameon=False)
        rax.axis('off')

        visualizer = cycle(
            (
                Visualizer(row[col], 3),
                Visualizer(row[col], 1)
            )
        )


        def switch_graph(images):
            img_png = cairosvg.svg2png(url=str(images))
            img = Image.open(BytesIO(img_png))
            axx.imshow(img)
            print('New image')
            fig.canvas.draw()

        switch_graph(next(visualizer))

        resistance_df = pd.DataFrame.from_dict({
            'r1': [row[col].resistance_r1],
            'x1': [row[col].reactance_x1],
            'r0': [row[col].resistance_r0],
            'x0': [row[col].reactance_x0]
        })

        resistance_table = ax[col][idx].table(
            cellText=resistance_df.values, colLabels=resistance_df.columns,
            loc='center', cellLoc='center', bbox=[0.2, 0.5, 0.8, 0.5], fontsize='large',
            colColours=('#9999FF',) * len(resistance_df.columns),
            cellColours=(('#CCCCFF',) * len(resistance_df.columns),) * len(resistance_df.index))

        short_circuit_df = cycle(
            (
                pd.DataFrame.from_dict({
                    'I_k(3)': [Calculator(row[:col + 1]).three_phase_current_short_circuit],
                    'I_k(2)': [Calculator(row[:col + 1]).two_phase_voltage_short_circuit],
                    'I_k(1)': [Calculator(row[:col + 1]).one_phase_voltage_short_circuit]
                }),
                pd.DataFrame.from_dict({
                    'I_k(3)': ['-----'],
                    'I_k(2)': ['-----'],
                    'I_k(1)': [Calculator(row[:col + 1]).one_phase_voltage_short_circuit]
                })
            )
        )

        short_circuit_table = ax[col][idx].table(
            cellText=next(short_circuit_df).values, colLabels=next(short_circuit_df).columns,
            loc='center', cellLoc='center', bbox=[0.4, 0, 0.6, 0.5], fontsize='large',
            colColours=('#FFCC99',) * len(next(short_circuit_df).columns),
            cellColours=(('#FFE5CC',) * len(next(short_circuit_df).columns),) * len(next(short_circuit_df).index))

        check = CheckButtons(rax, ['3ph'], [True])
        check.on_clicked(lambda label, i=col, j=idx: callback(label, i, j))
        Button = namedtuple('Button', ['check', 'labels', 'visibility', 'visual', 'sc_data', 'pic', 'tabl'])
        checks[col, idx] = Button(check, ['3ph'], [True], visualizer, short_circuit_df, switch_graph, short_circuit_table)


def callback(label, i, j):
    if label == '3ph':
        print(f'label: {label}, i: {i}, j: {j}')
        # print(f'pic before: {checks[i, j].pic}')
        # print(f'table before: {checks[i, j].tabl}')
        a = next(checks[i, j].visual)
        print(f'graph before {a}')
        checks[i, j].pic(a)
        # print(f'pic after: {checks[i, j].pic}')
        # print(f'table after: {checks[i, j].tabl}')
        fig.canvas.draw()


# Turn off axis
for idx, row in enumerate(schem):
    for col in range(max(map(len, schem))):
        ax[col][idx].axis('off')

fig.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.resultView.set_figure(fig)
w.show()
app.exec_()
