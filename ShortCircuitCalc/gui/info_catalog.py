# -*- coding: utf-8 -*-
"""The module provides a reference catalog of parameters of
electrical equipment presented in the program database."""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec, figure

from ShortCircuitCalc.database import *
from ShortCircuitCalc.config import GUI_DIR


__all__ = ('info_catalog_figure',)


def info_catalog_figure() -> figure.Figure:
    background_image = plt.imread(GUI_DIR / 'resources' / 'images' / 'info_catalog_back.jpg')
    table_transparency = 0.7

    # Creating the dataframe for transformers info in catalog
    power_col = PowerNominal.read_table().loc[:, 'power']
    voltage_col = VoltageNominal.read_table().loc[:, 'voltage']
    vector_group_col = Scheme.read_table().loc[:, 'vector_group']
    transformers_df = pd.concat((power_col, voltage_col, vector_group_col), axis=1).replace(np.nan, '---')

    # Creating the dataframe for cables/wires info in catalog
    mark_col = Mark.read_table().loc[:, 'mark_name']
    multicore_amount_col = Amount.read_table().loc[:, 'multicore_amount']
    range_col = RangeVal.read_table().loc[:, 'cable_range']
    cables_df = pd.concat((mark_col, multicore_amount_col, range_col), axis=1).replace(np.nan, '---')

    # Creating the dataframe for circuit breaker devices info in catalog
    device_col = Device.read_table().loc[:, 'device_type']
    current_nominal_col = CurrentNominal.read_table().loc[:, 'current_value']
    current_breakers_df = pd.concat((device_col, current_nominal_col), axis=1).replace(np.nan, '---')

    # Creating the dataframe for other contacts info in catalog
    other_contacts_df = pd.DataFrame(OtherContact.read_table().loc[:, 'contact_type'])

    # Creating info catalog gui
    figsize_x = sum((len(transformers_df.columns), len(cables_df.columns),
                     len(current_breakers_df.columns), len(other_contacts_df.columns))) + 2
    figsize_y = (max((len(transformers_df.index), len(cables_df.index),
                      len(current_breakers_df.index), len(other_contacts_df.index))) + 1) * 0.4
    fig = plt.figure(figsize=(figsize_x, figsize_y))
    fig.patch.set_facecolor('#FFFFCC')
    spec = gridspec.GridSpec(nrows=1, ncols=9)

    # Transformers plot properties
    ax0 = fig.add_subplot(spec[0, 0:3])
    ax0.axis('off')
    ax0.set_title('Transformers').set_bbox(dict(facecolor='#9999FF', alpha=table_transparency))

    transformers_table = ax0.table(
        cellText=transformers_df.values, colLabels=transformers_df.columns,
        loc='center', cellLoc='center', bbox=[0, 0, 1, 1],
        colColours=('#9999FF',) * len(transformers_df.columns),
        cellColours=(('#CCCCFF',) * len(transformers_df.columns),) * len(transformers_df.index))

    transformers_table.auto_set_column_width(col=list(range(len(transformers_df.columns))))

    # Cables/wires plot properties
    ax1 = fig.add_subplot(spec[0, 3:6])
    ax1.axis('off')
    ax1.set_title('Cables/wires').set_bbox(dict(facecolor='#FF9999', alpha=table_transparency))

    cables_table = ax1.table(
        cellText=cables_df.values, colLabels=cables_df.columns,
        loc='center', cellLoc='center', bbox=[0, 0, 1, 1],
        colColours=('#FF9999',) * len(cables_df.columns),
        cellColours=(('#FFCCCC',) * len(cables_df.columns),) * len(cables_df.index))

    cables_table.auto_set_column_width(col=list(range(len(cables_df.columns))))

    # Circuit breaker devices plot properties
    ax2 = fig.add_subplot(spec[0, 6:8])
    ax2.axis('off')
    ax2.set_title('Circuit breaker devices').set_bbox(dict(facecolor='#FFCC99', alpha=table_transparency))

    current_breakers_table = ax2.table(
        cellText=current_breakers_df.values, colLabels=current_breakers_df.columns,
        loc='center', cellLoc='center', bbox=[0, 0, 1, 1],
        colColours=('#FFCC99',) * len(current_breakers_df.columns),
        cellColours=(('#FFE5CC',) * len(current_breakers_df.columns),) * len(current_breakers_df.index))

    current_breakers_table.auto_set_column_width(col=list(range(len(current_breakers_df.columns))))

    # Other contacts plot properties
    ax3 = fig.add_subplot(spec[0, 8])
    ax3.axis('off')
    ax3.set_title('Other contacts').set_bbox(dict(facecolor='#CCFF99', alpha=table_transparency))

    other_contacts_table = ax3.table(
        cellText=other_contacts_df.values, colLabels=other_contacts_df.columns,
        loc='center', cellLoc='center', bbox=[0, 0.5, 1, 0.5],
        colColours=('#CCFF99',) * len(other_contacts_df.columns),
        cellColours=(('#E5FFCC',) * len(other_contacts_df.columns),) * len(other_contacts_df.index))

    other_contacts_table.auto_set_column_width(col=list(range(len(other_contacts_df.columns))))
    plt.tight_layout()

    # Creating background image
    # Make subplots semi-transparent
    for table in (transformers_table, cables_table, current_breakers_table, other_contacts_table):
        # noinspection PyProtectedMember
        for cell in table._cells:
            # noinspection PyProtectedMember
            table._cells[cell].set_alpha(table_transparency)
    background_ax = plt.axes([0, 0, 1, 1])  # create a subplot for the background
    background_ax.set_zorder(-1)  # set the background subplot behind the others
    background_ax.imshow(background_image, aspect='auto')  # show the backgroud image

    return fig
