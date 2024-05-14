"""Module text

For correctly working cairosvg first install and
add in PATH environment bin directory variables:
    - gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe;
    - uniconvertor-2.0rc4-win64_headless.msi"""


import sys
from io import BytesIO
from collections import namedtuple

import pandas as pd
from matplotlib import figure, axes
from matplotlib.widgets import CheckButtons
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5 import QtWidgets
import cairosvg
from PIL import Image

from ShortCircuitCalc.tools import *
from ShortCircuitCalc.gui import *
from ShortCircuitCalc.config import SYSTEM_PHASES


def results_figure():
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
    fig.canvas = FigureCanvasQTAgg(fig)
    ax = fig.canvas.figure.subplots(nrows, ncols)
    fig.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)

    def switch_and_draw_table(axe, h_pos, v_pos, df, switch_bool):
        return axe[h_pos][v_pos].table(
            cellText=df[switch_bool].values, colLabels=df[switch_bool].columns,
            loc='center', cellLoc='center', bbox=[0.4, 0, 0.6, 0.5],
            colColours=('#FFCC99',) * len(df[switch_bool].columns),
            cellColours=(('#FFE5CC',) * len(df[switch_bool].columns),) * len(df[switch_bool].index))

    checks = dict()
    for idx, row in enumerate(schem):
        for col in range(len(row)):
            axx = ax[col, idx].inset_axes([0, 0, 0.2, 1], anchor='SW')
            axx.axis('off')

            rax = fig.add_axes([axx.get_position().x0, axx.get_position().y0,
                                axx.get_position().width / 2, axx.get_position().height / 2],
                               frameon=False)
            rax.axis('off')

            resistance_df = pd.DataFrame.from_dict({
                'r1': [row[col].resistance_r1],
                'x1': [row[col].reactance_x1],
                'r0': [row[col].resistance_r0],
                'x0': [row[col].reactance_x0]
            })

            # noinspection PyUnusedLocal
            resistance_table = ax[col][idx].table(
                cellText=resistance_df.values, colLabels=resistance_df.columns,
                loc='center', cellLoc='center', bbox=[0.2, 0.5, 0.8, 0.5],
                colColours=('#9999FF',) * len(resistance_df.columns),
                cellColours=(('#CCCCFF',) * len(resistance_df.columns),) * len(resistance_df.index))

            background = fig.canvas.copy_from_bbox(ax[col][idx].bbox)

            images = [
                Image.open(BytesIO(
                    cairosvg.svg2png(url=str(Visualizer(row[col], SYSTEM_PHASES))))
                ),
                Image.open(BytesIO(
                    cairosvg.svg2png(url=str(Visualizer(row[col], SYSTEM_PHASES).create_invert)))
                )
            ]
            axx.imshow(images[0])

            short_circuit_df = [
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
            ]

            short_circuit_table = [
                switch_and_draw_table(
                    ax, col, idx, short_circuit_df, SYSTEM_PHASES != 3
                )
            ]

            check = CheckButtons(rax, ['3ph'], [SYSTEM_PHASES == 3], label_props={'color': 'red'})
            check.on_clicked(lambda label, i=col, j=idx: callback(label, i, j))
            Button = namedtuple(
                'Button', ('check', 'ax', 'rax', 'images', 'sc_df', 'sc_table', 'back')
            )
            checks[col, idx] = Button(
                check, ax[col, idx], rax, images, short_circuit_df, short_circuit_table, background
            )

    # noinspection PyUnusedLocal
    def callback(label, i, j):
        # Replace graph
        temp_axx = [c for c in checks[i, j].ax.get_children() if isinstance(c, axes.Axes)][0]
        temp_img = checks[i, j].images.pop()
        checks[i, j].images.insert(0, temp_img)
        temp_axx.images[0].set_data(temp_img)

        # Replace table view
        ax_objects = checks[i, j].ax.get_children()
        ax_objects[ax_objects.index(checks[i, j].sc_table[0])].remove()
        checks[i, j].sc_table.clear()
        new_table = switch_and_draw_table(
            ax, i, j, checks[i, j].sc_df, not checks[i, j].check.get_status()[0]
        )
        ax_objects.append(new_table)
        checks[i, j].sc_table.append(new_table)

        # Blitting / fast refreshing fig
        fig.canvas.restore_region(checks[i, j].back)
        fig.draw_artist(checks[i, j].ax)
        fig.draw_artist(checks[i, j].rax)
        fig.canvas.blit(checks[i, j].ax.bbox)
        fig.canvas.flush_events()

    # Turn off axis
    for idx, row in enumerate(schem):
        for col in range(max(map(len, schem))):
            ax[col][idx].axis('off')

    fig.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)

    return fig


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resultView.set_figure(results_figure())
    w.show()
    app.exec_()
