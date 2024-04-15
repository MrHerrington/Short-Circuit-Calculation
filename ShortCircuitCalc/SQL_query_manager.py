# -*- coding: utf-8 -*-
"""This module uses for managing custom SQL queries in the database."""


from ShortCircuitCalc.tools import session_scope
from ShortCircuitCalc.tools import elements


with session_scope() as session:
    pass


a = getattr(elements, 'W')('ВВГ', 3, '16', '20')
print(a)
