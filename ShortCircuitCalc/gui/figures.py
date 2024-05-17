"""Module text

For correctly working cairosvg first install and
add in PATH environment bin directory variables:
    - gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe;
    - uniconvertor-2.0rc4-win64_headless.msi"""


import sys
import typing as ty
from io import BytesIO
from collections import namedtuple
from functools import singledispatchmethod

import logging
import pandas as pd
from matplotlib import figure, axes
from matplotlib.widgets import CheckButtons
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5 import QtWidgets
import cairosvg
from PIL import Image

from ShortCircuitCalc.tools import *
from ShortCircuitCalc.gui import *
from ShortCircuitCalc.config import SYSTEM_PHASES, GRAPHS_DIR


__all__ = ('ResultsFigure',)


logger = logging.getLogger(__name__)


class Visualizer:
    __PHASES_LIST = (1, 3)

    def __init__(self, element, phases_default):
        self._element = element
        self._phases_default = phases_default
        self._graphs = {

            (T, 3, 'У/Ун-0'): GRAPHS_DIR / 'T_star_three.svg',
            (T, 1, 'У/Ун-0'): GRAPHS_DIR / 'T_star_one.svg',
            (T, 3, 'Д/Ун-11'): GRAPHS_DIR / 'T_triangle_three.svg',
            (T, 1, 'Д/Ун-11'): GRAPHS_DIR / 'T_triangle_one.svg',

            (Q, 3): GRAPHS_DIR / 'Q_three.svg',
            (Q, 1): GRAPHS_DIR / 'Q_one.svg',
            (QF, 3): GRAPHS_DIR / 'QF_three.svg',
            (QF, 1): GRAPHS_DIR / 'QF_one.svg',
            (QS, 3): GRAPHS_DIR / 'QS_three.svg',
            (QS, 1): GRAPHS_DIR / 'QS_one.svg',

            (W, 3): GRAPHS_DIR / 'W_three.svg',
            (W, 1): GRAPHS_DIR / 'W_one.svg',

            (R, 3): GRAPHS_DIR / 'R_three.svg',
            (R, 1): GRAPHS_DIR / 'R_one.svg',
            (Line, 3): GRAPHS_DIR / 'Line_three.svg',
            (Line, 1): GRAPHS_DIR / 'Line_one.svg',
            (Arc, 3): GRAPHS_DIR / 'Arc_three.svg',
            (Arc, 1): GRAPHS_DIR / 'Arc_one.svg',

        }

    @singledispatchmethod
    def _display_element(self, element):
        logger.error(f'Unknown type of element: {type(element)}')
        raise NotImplementedError

    @_display_element.register(T)
    def _(self, element):
        return self._graphs[element.__class__, self._phases_default, self._element.vector_group]

    @_display_element.register(Q)
    @_display_element.register(W)
    @_display_element.register(R)
    def _(self, element):
        return self._graphs[element.__class__, self._phases_default]

    @property
    def create_invert(self):
        if self._phases_default == Visualizer.__PHASES_LIST[1]:
            __phases = Visualizer.__PHASES_LIST[0]
        else:
            __phases = Visualizer.__PHASES_LIST[1]
        return Visualizer(self._element, __phases)

    def __repr__(self):
        return f'{self._display_element(self._element)}'


class ResultsFigure:
    def __new__(cls, *args, **kwargs):
        return _ResultsFigure(*args, **kwargs).fig


class _ResultsFigure:
    def __init__(self, schem):
        self.schem = schem

        self.nrows = max(map(len, self.schem))
        self.ncols = len(self.schem)

        self.fig = figure.Figure(figsize=(self.ncols * 5, self.nrows * 1))
        self.fig.canvas = FigureCanvasQTAgg(self.fig)

        self.ax = self.fig.canvas.figure.subplots(self.nrows, self.ncols)
        if len(self.schem) == 1:
            self.ax = self.ax.reshape(-1, 1)

        self.checks = dict()

        self.fig.subplots_adjust(wspace=0.01, hspace=0, left=0, right=1, bottom=0, top=1)
        self.__draw_figure()
        self.__off_axis()
        self.fig.subplots_adjust(wspace=0.01, hspace=0, left=0, right=1, bottom=0, top=1)

    def __draw_figure(self):
        for idx, row in enumerate(self.schem):
            for col in range(len(row)):
                self.__draw_cell_sequence(idx, row, col)

    def __draw_cell_sequence(self, idx, row, col):
        axx = self.ax[col, idx].inset_axes([0, 0, 0.2, 1], anchor='SW')
        axx.axis('off')

        rax = self.fig.add_axes([axx.get_position().x0, axx.get_position().y0,
                                 axx.get_position().width / 2, axx.get_position().height / 2],
                                frameon=False)
        rax.axis('off')

        if isinstance(row[col], (T, W)):
            self.ax[col][idx].text(
                0.3, 0.375, ' '.join(str(row[col]).split()[:2]), ha='center', va='center', fontsize=9, weight='bold'
            )
            self.ax[col][idx].text(
                0.3, 0.125, str(row[col]).split()[-1], ha='center', va='center', fontsize=9, weight='bold'
            )
        else:
            self.ax[col][idx].text(
                0.3, 0.25, str(row[col]), ha='center', va='center', fontsize=9, weight='bold'
            )

        resistance_df = pd.DataFrame.from_dict({
            'r1': [row[col].resistance_r1],
            'x1': [row[col].reactance_x1],
            'r0': [row[col].resistance_r0],
            'x0': [row[col].reactance_x0]
        })

        # noinspection PyUnusedLocal
        resistance_table = self.ax[col][idx].table(
            cellText=resistance_df.values, colLabels=resistance_df.columns,
            loc='center', cellLoc='center', bbox=[0.2, 0.5, 0.8, 0.5],
            colColours=('#9999FF',) * len(resistance_df.columns),
            cellColours=(('#CCCCFF',) * len(resistance_df.columns),) * len(resistance_df.index))

        background = self.fig.canvas.copy_from_bbox(self.ax[col][idx].bbox)

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
                'I_k(3)': [ElemChain(row[:col + 1]).three_phase_current_short_circuit],
                'I_k(2)': [ElemChain(row[:col + 1]).two_phase_current_short_circuit],
                'I_k(1)': [ElemChain(row[:col + 1]).one_phase_current_short_circuit]
            }),
            pd.DataFrame.from_dict({
                'I_k(3)': ['-----'],
                'I_k(2)': ['-----'],
                'I_k(1)': [ElemChain(row[:col + 1]).one_phase_current_short_circuit]
            })
        ]

        short_circuit_table = [
            self.__redraw_table(
                self.ax, col, idx, short_circuit_df, SYSTEM_PHASES != 3
            )
        ]

        check = CheckButtons(rax, ['3ph'], [SYSTEM_PHASES == 3], label_props={'color': 'red'})
        check.on_clicked(lambda label, i=col, j=idx: self.__callback(label, i, j))
        Button = namedtuple(
            'Button', ('check', 'ax', 'rax', 'images', 'sc_df', 'sc_table', 'back')
        )
        self.checks[col, idx] = Button(
            check, self.ax[col, idx], rax, images, short_circuit_df, short_circuit_table, background
        )

    def __draw_cell_mapping(self, idx, row, col):
        pass
        # if isinstance(row, ty.Mapping):
        #     resistance_df = pd.DataFrame.from_dict({
        #         'r1': [tuple(row.values())[col].resistance_r1],
        #         'x1': [tuple(row.values())[col].reactance_x1],
        #         'r0': [tuple(row.values())[col].resistance_r0],
        #         'x0': [tuple(row.values())[col].reactance_x0]
        #     })

    # noinspection PyUnusedLocal
    def __callback(self, label, i, j):
        # Replace graph
        temp_axx = [c for c in self.checks[i, j].ax.get_children() if isinstance(c, axes.Axes)][0]
        temp_img = self.checks[i, j].images.pop()
        self.checks[i, j].images.insert(0, temp_img)
        temp_axx.images[0].set_data(temp_img)

        # Replace table view
        ax_objects = self.checks[i, j].ax.get_children()
        ax_objects[ax_objects.index(self.checks[i, j].sc_table[0])].remove()
        self.checks[i, j].sc_table.clear()
        new_table = self.__redraw_table(
            self.ax, i, j, self.checks[i, j].sc_df, not self.checks[i, j].check.get_status()[0]
        )
        ax_objects.append(new_table)
        self.checks[i, j].sc_table.append(new_table)

        # Blitting / fast refreshing fig
        self.fig.canvas.restore_region(self.checks[i, j].back)
        self.fig.draw_artist(self.checks[i, j].ax)
        self.fig.draw_artist(self.checks[i, j].rax)
        self.fig.canvas.blit(self.checks[i, j].ax.bbox)
        self.fig.canvas.flush_events()

    def __off_axis(self):
        for idx, row in enumerate(self.schem):
            for col in range(self.nrows):
                self.ax[col][idx].axis('off')

    @staticmethod
    def __redraw_table(axe, h_pos, v_pos, df, switch_bool):
        return axe[h_pos][v_pos].table(
            cellText=df[switch_bool].values, colLabels=df[switch_bool].columns,
            loc='center', cellLoc='center', bbox=[0.4, 0, 0.6, 0.5],
            colColours=('#FFCC99',) * len(df[switch_bool].columns),
            cellColours=(('#FFE5CC',) * len(df[switch_bool].columns),) * len(df[switch_bool].index))
