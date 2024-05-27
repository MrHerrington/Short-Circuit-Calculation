from ShortCircuitCalc.database import *
import sqlalchemy as sa
from tools import session_scope


# Transformer.read_joined_table()
# Transformer.insert_joined_table([
#     {
#         'power': 2000,
#         'voltage': 0.4,
#         'vector_group': 'Жопа',
#         'power_short_circuit': 0.1,
#         'voltage_short_circuit': 0.1,
#         'resistance_r1': 0.01,
#         'reactance_x1': 0.01,
#         'resistance_r0': 0.01,
#         'reactance_x0': 0.01
#     }
# ])
# print(*PowerNominal.get_all_keys(as_str=False))
# print(PowerNominal.get_primary_key(as_str=False))
# print(Transformer.get_foreign_keys(on_side=False, as_str=True))
# print(Transformer.get_non_keys(as_str=False)[0])
# print(Transformer.read_joined_table())
print(Transformer.update_joined_table(row_id=15, old_source_data={
                                          'power': 100,
                                          'voltage': 0.4,
                                          'vector_group': 'У/Ун-0'
                                      }
                                      )
      )
# print(PowerNominal.reset_id())
# print(Transformer.reset_id())
# print(PowerNominal.update_table([{'id': 1, 'power': 5000}]))
