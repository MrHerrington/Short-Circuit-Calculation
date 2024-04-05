from ShortCircuitCalc.database.transformer import *
from ShortCircuitCalc.database.cable import *
from ShortCircuitCalc.database.contact import *
from config import DATA_DIR


if __name__ == '__main__':
    PowerNominal.create_table(drop_first=True, forced_drop=True)
    PowerNominal.insert_table(from_csv=DATA_DIR/'transformer_catalog'/'power_nominal')

    VoltageNominal.create_table(drop_first=True, forced_drop=True)
    VoltageNominal.insert_table(from_csv=DATA_DIR/'transformer_catalog'/'voltage_nominal')

    Scheme.create_table(drop_first=True, forced_drop=True)
    Scheme.insert_table(from_csv=DATA_DIR/'transformer_catalog'/'scheme')

    Transformer.create_table(drop_first=True)
    Transformer.insert_table(from_csv=DATA_DIR/'transformer_catalog'/'transformer')

    Mark.create_table(drop_first=True, forced_drop=True)
    Mark.insert_table(from_csv=DATA_DIR/'cable_catalog'/'mark')

    Amount.create_table(drop_first=True, forced_drop=True)
    Amount.insert_table(from_csv=DATA_DIR/'cable_catalog'/'amount')

    RangeVal.create_table(drop_first=True, forced_drop=True)
    RangeVal.insert_table(from_csv=DATA_DIR/'cable_catalog'/'range')

    Cable.create_table(drop_first=True)
    Cable.insert_table(from_csv=DATA_DIR/'cable_catalog'/'cable')
