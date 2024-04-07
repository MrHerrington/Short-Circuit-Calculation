"""This module performs the initial deployment of the database, including the creation
of basic lookup tables and their filling from equipment parameter catalogs"""


import typing as ty
import pathlib
from tools import engine, metadata
from config import DATA_DIR
from ShortCircuitCalc.database.transformer import *
from ShortCircuitCalc.database.cable import *
from ShortCircuitCalc.database.contact import *


def deploy_if_not_exist(table: Base, pathlike: ty.Union[str, pathlib.WindowsPath] = None) -> None:
    """Function to deploy a table if it does not already exist in the database.

    Args:
        table (Base): The table object to deploy.
        pathlike (Union[str, pathlib.WindowsPath], optional): The path to the CSV file. Defaults to None.

    """
    metadata.reflect(bind=engine)
    if table.__tablename__ not in metadata.tables:
        table.create_table()
        table.insert_table(from_csv=pathlike)


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
