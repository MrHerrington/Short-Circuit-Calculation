# -*- coding: utf-8 -*-
"""
This module uses for managing custom SQL queries in the database.

"""


# noinspection PyUnresolvedReferences
from shortcircuitcalc.database import (
    PowerNominal, VoltageNominal, Scheme, Transformer,
    Mark, Amount, RangeVal, Cable,
    Device, CurrentNominal, CurrentBreaker,
    OtherContact
)
from shortcircuitcalc.tools import session_scope


with session_scope() as session:
    pass
