# -*- coding: utf-8 -*-
"""
This module performs the initial deployment of the database,
including the creation of basic lookup tables and their
filling from equipment parameter catalogs

"""


import typing as ty
from pathlib import Path

import sqlalchemy as sa
import sqlalchemy.exc

from shortcircuitcalc.database.models import (
    PowerNominal, VoltageNominal, Scheme, Transformer,
    Mark, Amount, RangeVal, Cable,
    Device, CurrentNominal, CurrentBreaker,
    OtherContact
)
from shortcircuitcalc.tools import (
    Base, engine, metadata, session_scope, config_manager
)
from shortcircuitcalc.config import DATA_DIR


__all__ = ('db_install',)


def deploy_if_not_exist(db_table: ty.Type[Base],
                        pathlike: ty.Union[str, Path],
                        full: bool = False
                        ) -> None:
    """Function to deploy a table if it does not already exist in the database.

    Args:
        db_table (Base): The table object to deploy.
        pathlike (Union[str, pathlib.WindowsPath]): The path to the CSV file. Defaults to None.
        full (bool): If True, the table will be dropped and recreated with data from CSV file. Defaults to None.

    """
    try:
        metadata.reflect(bind=engine)

        if full or db_table.__tablename__ not in metadata.tables:
            db_table.create_table(drop_first=full, forced_drop=full)
            db_table.insert_table(from_csv=pathlike)

    except sqlalchemy.exc.NoSuchTableError:
        db_table.create_table()
        db_table.insert_table(from_csv=pathlike)


def db_install(clear: bool = False) -> None:
    """Deploy part of the database for different equipment categories.

    Args:
        clear (bool): If True, clear existing data before deployment.

    """
    # Need for create SQLITE_SEQUENCE in DB
    if config_manager('DB_EXISTING_CONNECTION') == 'SQLite':
        with session_scope() as session:
            session.execute(sa.text("CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT);"))
            session.execute(sa.text("DROP TABLE test;"))

    # Deploying part of the database for equipment category 'Transformers'
    for table in (PowerNominal, VoltageNominal, Scheme, Transformer):
        deploy_if_not_exist(table, DATA_DIR / 'transformer_catalog' / Path(table.__tablename__ + 's'), clear)

    # Deploying part of the database for equipment category 'Cables and wires'
    for table in (Mark, Amount, RangeVal, Cable):
        deploy_if_not_exist(table, DATA_DIR / 'cable_catalog' / Path(table.__tablename__ + 's'), clear)

    # Deploying part of the database for equipment category 'Current breaker devices'
    for table in (Device, CurrentNominal, CurrentBreaker):
        deploy_if_not_exist(table, DATA_DIR / 'current_breaker_catalog' / Path(table.__tablename__ + 's'), clear)

    # Deploying part of the database for equipment category 'Other resistances'
    deploy_if_not_exist(OtherContact, DATA_DIR / Path(OtherContact.__tablename__ + 's'), clear)
