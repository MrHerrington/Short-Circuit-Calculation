"""This module performs the initial deployment of the database, including the creation
of basic lookup tables and their filling from equipment parameter catalogs"""


from ShortCircuitCalc.database.transformer import *
from ShortCircuitCalc.database.cable import *
from ShortCircuitCalc.database.contact import *
from config import DATA_DIR


if __name__ == '__main__':

    # Deploying part of the database for equipment category 'Transformers'
    PowerNominal.create_table(drop_first=True, forced_drop=True)
    PowerNominal.insert_table(from_csv=DATA_DIR/'transformer_catalog'/'power_nominal')

    VoltageNominal.create_table(drop_first=True, forced_drop=True)
    VoltageNominal.insert_table(from_csv=DATA_DIR/'transformer_catalog'/'voltage_nominal')

    Scheme.create_table(drop_first=True, forced_drop=True)
    Scheme.insert_table(from_csv=DATA_DIR/'transformer_catalog'/'scheme')

    Transformer.create_table(drop_first=True)
    Transformer.insert_table(from_csv=DATA_DIR/'transformer_catalog'/'transformer')

    # Deploying part of the database for equipment category 'Cables and wires'
    Mark.create_table(drop_first=True, forced_drop=True)
    Mark.insert_table(from_csv=DATA_DIR/'cable_catalog'/'mark')

    Amount.create_table(drop_first=True, forced_drop=True)
    Amount.insert_table(from_csv=DATA_DIR/'cable_catalog'/'amount')

    RangeVal.create_table(drop_first=True, forced_drop=True)
    RangeVal.insert_table(from_csv=DATA_DIR/'cable_catalog'/'range')

    Cable.create_table(drop_first=True)
    Cable.insert_table(from_csv=DATA_DIR/'cable_catalog'/'cable')

    # Deploying part of the database for equipment category 'Current breaker devices'
    Device.create_table(drop_first=True, forced_drop=True)
    Device.insert_table(from_csv=DATA_DIR/'current_breaker_catalog'/'device')

    CurrentNominal.create_table(drop_first=True, forced_drop=True)
    CurrentNominal.insert_table(from_csv=DATA_DIR/'current_breaker_catalog'/'device')

    CurrentBreaker.create_table(drop_first=True)
    CurrentBreaker.insert_table(from_csv=DATA_DIR/'current_breaker_catalog'/'device')

    # Deploying part of the database for equipment category 'Other resistances'
    OtherContact.create_table(drop_first=True)
    OtherContact.insert_table(from_csv=DATA_DIR/'other_resistance')
