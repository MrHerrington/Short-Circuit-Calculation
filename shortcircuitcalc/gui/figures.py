# -*- coding: utf-8 -*-
"""
Module contains classes for drawing matplotlib figures in the GUI PyQt5.

For correctly working cairosvg first install and
add in PATH environment bin directory variables:
    - gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe;
    - uniconvertor-2.0rc4-win64_headless.msi

"""


import typing as ty
from io import BytesIO
from collections import namedtuple
from functools import singledispatchmethod

import logging
import numpy as np
import pandas as pd
from matplotlib import figure, axes, gridspec, image
from matplotlib.widgets import CheckButtons
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import cairosvg
from PIL import Image

from shortcircuitcalc.tools import (
    BaseElement,
    T, Q, QF, QS, W, R, Line, Arc,
    ChainsSystem, ElemChain
)
from shortcircuitcalc.database import (
    PowerNominal, VoltageNominal, Scheme,
    Mark, Amount, RangeVal,
    Device, CurrentNominal,
    OtherContact
)
from shortcircuitcalc.config import (
    SYSTEM_PHASES, GRAPHS_DIR, GUI_DIR
)


__all__ = ('GetFigure',)


logger = logging.getLogger(__name__)


BaseElem = ty.TypeVar('BaseElem', bound=BaseElement)


class Visualizer:
    """Class returns an object path for drawing an element in the GUI."""
    __PHASES_LIST = (1, 3)

    def __init__(self, element: BaseElem, phases_default: int):
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
    def _display_element(self, element: BaseElem) -> None:
        logger.error(f'Unknown type of element: {type(element)}')
        raise NotImplementedError

    @_display_element.register(T)
    def _(self, element: BaseElem) -> str:
        return self._graphs[element.__class__, self._phases_default, self._element.vector_group]

    @_display_element.register(Q)
    @_display_element.register(W)
    @_display_element.register(R)
    def _(self, element: BaseElem) -> str:
        return self._graphs[element.__class__, self._phases_default]

    @property
    def create_invert(self):
        """Create an inverted object path for drawing an element in the GUI."""
        if self._phases_default == Visualizer.__PHASES_LIST[1]:
            __phases = Visualizer.__PHASES_LIST[0]
        else:
            __phases = Visualizer.__PHASES_LIST[1]
        return Visualizer(self._element, __phases)

    def __repr__(self):
        return f'{self._display_element(self._element)}'


class GetFigure:
    """Class-manager for creating figures in the GUI.

    if arg is None, return figure for catalog window,
    else return figure for results window.

    """
    def __new__(cls, obj=None):
        if obj is None:
            return _CatalogFigure().fig
        else:
            return _ResultsFigure(obj)


class _ResultsFigure:
    """Service class for drawing results figure."""
    def __init__(self, schem: ChainsSystem):
        self.schem = schem

        self.nrows = max(map(len, self.schem))
        self.ncols = len(self.schem)

        self.fig = figure.Figure(figsize=(self.ncols * 5, self.nrows * 1))
        self.fig.canvas = FigureCanvasQTAgg(self.fig)

        self.ax = self.fig.canvas.figure.subplots(self.nrows, self.ncols, squeeze=False)

        self.checks = dict()

        self.fig.subplots_adjust(wspace=0.01, hspace=0, left=0.01, right=0.99, bottom=0.01, top=0.99)
        self.__draw_figure()
        self.__off_axis()
        self.fig.subplots_adjust(wspace=0.01, hspace=0, left=0.01, right=0.99, bottom=0.01, top=0.99)

        logger.info('Results system successfully created %s' % self.schem)

    def __draw_figure(self) -> None:
        """Draw all elements in the figure."""
        for idx, row in enumerate(self.schem):
            for col in range(len(row)):
                self.__draw_cells(idx, row, col)

    def __draw_cells(self, idx: int, row: ElemChain, col: int) -> None:
        """Contain one cell configuration.

        Draw one cell in the figure, including:
        - element label and project name if exists,
        - element graph,
        - element resists table,
        - element short circuit current values.

        """
        iter_values = None
        map_keys = None
        map_values = None

        if isinstance(row.obj, ty.Mapping):
            map_keys = tuple(row.obj.keys())
            map_values = tuple(row.obj.values())
        else:
            iter_values = row

        h_align = 'center'
        v_align = 'center'
        f_size = 9
        f_weight = 'bold'

        axx = self.ax[col, idx].inset_axes([0, 0, 0.2, 1], anchor='SW')
        axx.axis('off')

        rax = self.fig.add_axes([axx.get_position().x0, axx.get_position().y0,
                                 axx.get_position().width / 2, axx.get_position().height / 2],
                                frameon=False)
        rax.axis('off')

        if isinstance(row.obj, ty.Mapping):
            if isinstance(map_values[col], (T, W)):
                self.ax[col][idx].text(
                    0.3, 0.375, map_keys[col],
                    ha=h_align, va=v_align, fontsize=f_size, weight=f_weight
                )
                self.ax[col][idx].text(
                    0.3, 0.25, ' '.join(str(map_values[col]).split()[:2]),
                    ha=h_align, va=v_align, fontsize=f_size, weight=f_weight
                )
                self.ax[col][idx].text(
                    0.3, 0.125, str(map_values[col]).split()[-1],
                    ha=h_align, va=v_align, fontsize=f_size, weight=f_weight
                )
            else:
                self.ax[col][idx].text(
                    0.3, 0.375, map_keys[col],
                    ha=h_align, va=v_align, fontsize=f_size, weight=f_weight
                )
                self.ax[col][idx].text(
                    0.3, 0.125, str(map_values[col]),
                    ha=h_align, va=v_align, fontsize=f_size, weight=f_weight
                )
        else:
            if isinstance(iter_values[col], (T, W)):
                self.ax[col][idx].text(
                    0.3, 0.375, ' '.join(str(iter_values[col]).split()[:2]),
                    ha=h_align, va=v_align, fontsize=f_size, weight=f_weight
                )
                self.ax[col][idx].text(
                    0.3, 0.125, str(iter_values[col]).split()[-1],
                    ha=h_align, va=v_align, fontsize=f_size, weight=f_weight
                )
            else:
                self.ax[col][idx].text(
                    0.3, 0.25, str(iter_values[col]),
                    ha=h_align, va=v_align, fontsize=f_size, weight=f_weight
                )

        def __get_resistance_df(vals: ty.Sequence) -> pd.DataFrame:
            return pd.DataFrame.from_dict({
                'r1': [vals[col].resistance_r1],
                'x1': [vals[col].reactance_x1],
                'r0': [vals[col].resistance_r0],
                'x0': [vals[col].reactance_x0]
            })

        if isinstance(row.obj, ty.Mapping):
            resistance_df = __get_resistance_df(map_values)
        else:
            resistance_df = __get_resistance_df(iter_values)

        # noinspection PyUnusedLocal
        resistance_table = self.ax[col][idx].table(
            cellText=resistance_df.values, colLabels=resistance_df.columns,
            loc='center', cellLoc='center', bbox=[0.2, 0.5, 0.8, 0.5],
            colColours=('#9999FF',) * len(resistance_df.columns),
            cellColours=(('#CCCCFF',) * len(resistance_df.columns),) * len(resistance_df.index))

        background = self.fig.canvas.copy_from_bbox(self.ax[col][idx].bbox)

        def __get_images(vals: ty.Sequence) -> ty.List[Image.Image]:
            """Return images list with one/three phases element"""
            return [
                Image.open(BytesIO(
                    cairosvg.svg2png(url=str(Visualizer(vals[col], SYSTEM_PHASES))))
                ),
                Image.open(BytesIO(
                    cairosvg.svg2png(url=str(Visualizer(vals[col], SYSTEM_PHASES).create_invert)))
                )
            ]

        if isinstance(row.obj, ty.Mapping):
            images = __get_images(map_values)
        else:
            images = __get_images(iter_values)

        axx.imshow(images[0])

        def __get_short_circuit_df(vals: ty.Sequence) -> ty.List[pd.DataFrame]:
            """Return short circuit table with one/three phases element calculations"""
            return [
                pd.DataFrame.from_dict({
                    'I_k(3)': [ElemChain(vals[:col + 1]).three_phase_current_short_circuit],
                    'I_k(2)': [ElemChain(vals[:col + 1]).two_phase_current_short_circuit],
                    'I_k(1)': [ElemChain(vals[:col + 1]).one_phase_current_short_circuit]
                }),
                pd.DataFrame.from_dict({
                    'I_k(3)': ['-----'],
                    'I_k(2)': ['-----'],
                    'I_k(1)': [ElemChain(vals[:col + 1]).one_phase_current_short_circuit]
                })
            ]

        if isinstance(row.obj, ty.Mapping):
            short_circuit_df = __get_short_circuit_df(map_values)
        else:
            short_circuit_df = __get_short_circuit_df(iter_values)

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

    # noinspection PyUnusedLocal
    def __callback(self, label, i, j) -> None:
        """Check buttons callback.

        Replace graph / table calculations view.
        Also realize blitting / fast refreshing figure.

        """
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

    def __off_axis(self) -> None:
        """Turn off all axis."""
        for idx, row in enumerate(self.schem):
            for col in range(self.nrows):
                self.ax[col][idx].axis('off')

    @staticmethod
    def __redraw_table(axe: axes, h_pos: int, v_pos: int, df: ty.List[pd.DataFrame],
                       switch_bool: bool) -> axes.Axes:

        return axe[h_pos][v_pos].table(
            cellText=df[switch_bool].values, colLabels=df[switch_bool].columns,
            loc='center', cellLoc='center', bbox=[0.4, 0, 0.6, 0.5],
            colColours=('#FFCC99',) * len(df[switch_bool].columns),
            cellColours=(('#FFE5CC',) * len(df[switch_bool].columns),) * len(df[switch_bool].index))


class _CatalogFigure:
    """Service class for drawing catalog figure."""
    def __init__(self):
        self.fig = figure.Figure()
        self.grid = gridspec.GridSpec(nrows=1, ncols=9)
        self.table_transparency = 0.7
        self.background_image = image.imread(GUI_DIR / 'resources' / 'images' / 'info_catalog_back.jpg')
        self.dataframes = []
        self.__transformers_dataframe()
        self.__cables_dataframe()
        self.__devices_dataframe()
        self.__contacts_dataframe()
        self.__figure_options()
        self.__set_background()

    def __transformers_dataframe(self) -> None:
        """Draw transformers dataframe in catalog."""
        power_col = PowerNominal.read_table().loc[:, 'power']
        voltage_col = VoltageNominal.read_table().loc[:, 'voltage']
        vector_group_col = Scheme.read_table().loc[:, 'vector_group']
        transformers_df = pd.concat(
            (power_col, voltage_col, vector_group_col), axis=1
        ).replace(np.nan, '---')

        self.__set_dataframe(
            title='Transformers',
            grid=self.grid[0, 0:3],
            df=transformers_df,
            col_color='#9999FF',
            cell_color='#CCCCFF'
        )

    def __cables_dataframe(self):
        """Draw cables / wires dataframe in catalog."""
        mark_col = Mark.read_table().loc[:, 'mark_name']
        multicore_amount_col = Amount.read_table().loc[:, 'multicore_amount']
        range_col = RangeVal.read_table().loc[:, 'cable_range']
        cables_df = pd.concat((mark_col, multicore_amount_col, range_col), axis=1).replace(np.nan, '---')

        self.__set_dataframe(
            title='Cables / wires',
            grid=self.grid[0, 3:6],
            df=cables_df,
            col_color='#FF9999',
            cell_color='#FFCCCC'
        )

    def __devices_dataframe(self):
        """Draw devices dataframe in catalog."""
        device_col = Device.read_table().loc[:, 'device_type']
        current_nominal_col = CurrentNominal.read_table().loc[:, 'current_value']
        current_breakers_df = pd.concat(
            (device_col, current_nominal_col), axis=1
        ).replace(np.nan, '---')

        self.__set_dataframe(
            title='Circuit breaker devices',
            grid=self.grid[0, 6:8],
            df=current_breakers_df,
            col_color='#FFCC99',
            cell_color='#FFE5CC'
        )

    def __contacts_dataframe(self):
        """Draw contacts dataframe in catalog."""
        other_contacts_df = pd.DataFrame(OtherContact.read_table().loc[:, 'contact_type'])

        self.__set_dataframe(
            title='Other contacts',
            grid=self.grid[0, 8],
            df=other_contacts_df,
            col_color='#CCFF99',
            cell_color='#E5FFCC'
        )

    def __set_dataframe(self, title, grid, df, col_color, cell_color):
        """Set dataframe options."""
        ax = self.fig.add_subplot(grid)
        ax.axis('off')
        ax.set_title(title).set_bbox(dict(facecolor=col_color, alpha=self.table_transparency))

        table = ax.table(
            cellText=df.values, colLabels=df.columns,
            loc='center', cellLoc='center', bbox=[0, 0, 1, 1],
            colColours=(col_color,) * len(df.columns),
            cellColours=((cell_color,) * len(df.columns),) * len(df.index))

        table.auto_set_column_width(col=list(range(len(df.columns))))

        # noinspection PyProtectedMember
        for cell in table._cells:
            # noinspection PyProtectedMember
            table._cells[cell].set_alpha(self.table_transparency)

        self.dataframes.append(df)

    def __figure_options(self):
        """Set figure options."""
        figsize_x = sum(map(lambda x: len(x.columns), self.dataframes)) + 2
        figsize_y = (max(map(lambda x: len(x.index), self.dataframes)) + 1) * 0.4
        self.fig.set_size_inches(figsize_x, figsize_y)
        self.fig.patch.set_facecolor('#FFFFCC')
        self.fig.tight_layout()

    def __set_background(self):
        """Set background image in catalog."""
        # create a subplot for the background
        background_ax = self.fig.add_axes([0, 0, 1, 1])
        # set the background subplot behind the others
        background_ax.set_zorder(-1)
        # show the background image
        background_ax.imshow(self.background_image, aspect='auto')
