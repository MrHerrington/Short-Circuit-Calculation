from ShortCircuitCalc.database import *


# Transformer.read_joined_table()
Transformer.insert_joined_table([
    {
        'power': 2000,
        'voltage': 0.4,
        'vector_group': 'Жопа',
        'power_short_circuit': 0.1,
        'voltage_short_circuit': 0.1,
        'resistance_r1': 0.01,
        'reactance_x1': 0.01,
        'resistance_r0': 0.01,
        'reactance_x0': 0.01
    }
])
