"""This module uses for managing custom SQL queries in the database."""

from ShortCircuitCalc.database.transformer import *
from tools import session_scope

from decimal import Decimal

tst = (25, 0.4, 'У/Ун-0')

with session_scope() as session:
    res = session.execute(sa.select(Transformer.resistance_r1).
                          join(PowerNominal, Transformer.power_id == PowerNominal.id).
                          join(VoltageNominal, Transformer.voltage_id == VoltageNominal.id).
                          join(Scheme, Transformer.vector_group_id == Scheme.id).
                          where(sa.and_(PowerNominal.power == tst[0],
                                        VoltageNominal.voltage == Decimal(str(tst[1])),
                                        Scheme.vector_group == tst[2]))).scalar()
    print(res)
    pass
