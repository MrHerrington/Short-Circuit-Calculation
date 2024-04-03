import sqlalchemy as sa
from tools import Session
from tools import engine
from database.transformer import PowerNominal, VoltageNominal, Scheme, Transformer
import pandas as pd
import re

# with Session() as session:
#     for i in [25, 40, 63, 100, 160, 250, 400, 630, 1000, 1600]:
#         if i not in list(map(lambda x: x.power, session.query(PowerNominal))):
#             session.execute(sa.insert(PowerNominal), [{'power': i}])
#     session.commit()
#
# with Session() as session:
#     for i in [0.4]:
#         if i not in list(map(lambda x: x.voltage, session.query(VoltageNominal))):
#             session.execute(sa.insert(VoltageNominal), [{'voltage': i}])
#     session.commit()
#
# with Session() as session:
#     for i in ['У/Ун-0', 'Д/Ун-11']:
#         if i not in list(map(lambda x: x.vector_group, session.query(Scheme))):
#             session.execute(sa.insert(Scheme), [{'vector_group': i}])
#     session.commit()
#
# with Session() as session:
#     for i in [
#                 (1, 1, 1), (1, 1, 2),
#                 (2, 1, 1), (2, 1, 2),
#                 (3, 1, 1), (3, 1, 2),
#                 (4, 1, 1), (4, 1, 2),
#                 (5, 1, 1), (5, 1, 2),
#                 (6, 1, 1), (6, 1, 2),
#                 (7, 1, 1), (7, 1, 2),
#                 (8, 1, 1), (8, 1, 2),
#                 (9, 1, 1), (9, 1, 2),
#                 (10, 1, 1), (10, 1, 2),
#             ]:
#
#         if i not in list(map(lambda x: (x.power_id, x.voltage_id, x.vector_group_id),
#                              session.query(Transformer))):
#             session.execute(sa.insert(Transformer), [
#                                                         {'power_id': i[0],
#                                                          'voltage_id': i[1],
#                                                          'vector_group_id': i[2]}
#                                                     ])
#     session.commit()

# print(*PowerNominal.read_table('power', 1, 2, 3))

# with Session() as s:
#     question = s.query(getattr(PowerNominal, 'power'), VoltageNominal.voltage, Scheme.vector_group).\
#         select_from(Transformer).\
#         join(PowerNominal).\
#         join(VoltageNominal).\
#         join(Scheme).filter().limit()
#     for i in question:
#         print(i)

# a = PowerNominal.read_table(filtrate='power <= 63')
# print(a['power'].sum())
# PowerNominal.reset_auto_increment()
# PowerNominal.show_table()
# PowerNominal.reset_auto_increment()
# Transformer.reset_id()
# Transformer.show_table()
# PowerNominal.delete_table('power = 1000')
Transformer.create_table(True)