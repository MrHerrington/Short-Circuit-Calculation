# -*- coding: utf-8 -*-
"""This module performs the initial deployment of the database, including the creation
of basic lookup tables and their filling from equipment parameter catalogs"""


import typing as ty
from pathlib import Path

import sqlalchemy as sa

from ShortCircuitCalc.database import *
from ShortCircuitCalc.tools import *
from ShortCircuitCalc.config import DATA_DIR, DB_TABLES_CLEAR_INSTALL


def deploy_if_not_exist(db_table: ty.Type[Base], pathlike: ty.Union[str, Path],
                        full: bool = False) -> None:
    """Function to deploy a table if it does not already exist in the database.

    Args:
        db_table (Base): The table object to deploy.
        pathlike (Union[str, pathlib.WindowsPath]): The path to the CSV file. Defaults to None.
        full (bool): If True, the table will be dropped and recreated with data from CSV file. Defaults to None.

    """
    try:
        metadata.reflect(bind=engine)
    except sa.exc.NoSuchTableError:
        pass
    if full or db_table.__tablename__ not in metadata.tables:
        db_table.create_table(drop_first=full, forced_drop=full)
        db_table.insert_table(from_csv=pathlike)


def install(clear: bool = False) -> None:
    """Deploy part of the database for different equipment categories.

    Args:
        clear (bool): If True, clear existing data before deployment.

    """
    # Deploying part of the database for equipment category 'Transformers'
    for table in (PowerNominal,VoltageNominal, Scheme, Transformer):
        deploy_if_not_exist(table, DATA_DIR / 'transformer_catalog' / Path(table.__tablename__ + 's'), clear)

    # Deploying part of the database for equipment category 'Cables and wires'
    for table in (Mark, Amount, RangeVal, Cable):
        deploy_if_not_exist(table, DATA_DIR / 'cable_catalog' / Path(table.__tablename__ + 's'), clear)

    # Deploying part of the database for equipment category 'Current breaker devices'
    for table in (Device, CurrentNominal, CurrentBreaker):
        deploy_if_not_exist(table, DATA_DIR / 'current_breaker_catalog' / Path(table.__tablename__ + 's'), clear)

    # Deploying part of the database for equipment category 'Other resistances'
    deploy_if_not_exist(OtherContact, DATA_DIR / Path(OtherContact.__tablename__ + 's'), clear)


def installer():
    install(clear=DB_TABLES_CLEAR_INSTALL)


if __name__ == '__main__':
    installer()
