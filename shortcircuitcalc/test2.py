from shortcircuitcalc.database import CurrentBreaker
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
# Transformer.update_joined_table(
#     old_source_data={
#         'voltage': 0.4,
#         'power': 100,
#         'vector_group': 'У/Ун-0'
#     },
#     new_source_data={
#         'vector_group': 'У/Z-0',
#         'power': 6300
#     },
#     target_row_data={
#         'power_short_circuit': 0.11,
#         'voltage_short_circuit': 0.22,
#         'resistance_r1': 0.333,
#         'reactance_x1': 0.444,
#         'resistance_r0': 0.555,
#         'reactance_x0': 0.777
#     }
# )
# print(Transformer.update_joined_table(
#     old_source_data={
#         'voltage': 0.4,
#         'vector_group': 'У/Ун-0',
#         'power': 100
#
#     },
#     new_source_data={
#         'vector_group': 'Fisting',
#         'power': 1000000
#     }
# )
# )
# print(PowerNominal.reset_id())
# print(Transformer.reset_id())
# print(PowerNominal.update_table([{'id': 1, 'power': 5000}]))
# Transformer.update_joined_table()
# print(Transformer.read_joined_table())
# Transformer.delete_joined_table(
#     source_data={
#         'voltage': 0.4,
#         'vector_group': 'У/Ун-0',
#         'power': 100
#     },
#     from_source=True
# )
CurrentBreaker.delete_joined_table(source_data={'device_type': 'Рубильник'}, from_source=True)
# print(Transformer.get_join_stmt())
