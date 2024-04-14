# -*- coding: utf-8 -*-
"""This module uses for managing custom SQL queries in the database."""


from ShortCircuitCalc.tools import session_scope


with session_scope() as session:
    pass


from database import Transformer
Transformer.reset_id()