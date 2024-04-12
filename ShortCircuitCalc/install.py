"""This module performs the initial deployment of the database, including the creation
of basic lookup tables and their filling from equipment parameter catalogs"""


import typing as ty
import pathlib
from ShortCircuitCalc.tools import Base, engine, metadata
from ShortCircuitCalc.config import DATA_DIR, DB_TABLES_CLEAR_INSTALL
import ShortCircuitCalc.database as db


def deploy_if_not_exist(db_table: ty.Type[Base], pathlike: ty.Union[str, pathlib.WindowsPath],
                        full: bool = False) -> None:
    """Function to deploy a table if it does not already exist in the database.

    Args:
        db_table (Base): The table object to deploy.
        pathlike (Union[str, pathlib.WindowsPath]): The path to the CSV file. Defaults to None.
        full (bool): If True, the table will be dropped and recreated with data from CSV file. Defaults to None.

    """
    metadata.reflect(bind=engine)
    if full or db_table.__tablename__ not in metadata.tables:
        db_table.create_table(drop_first=full, forced_drop=full)
        db_table.insert_table(from_csv=pathlike)


def install(clear: bool = False) -> None:
    """Deploy part of the database for different equipment categories.

    Args:
        clear (bool): If True, clear existing data before deployment.

    """
    # Deploying part of the database for equipment category 'Transformers'
    for table in (db.PowerNominal, db.VoltageNominal, db.Scheme, db.Transformer):
        deploy_if_not_exist(table, DATA_DIR / 'transformer_catalog' / table.__tablename__, clear)

    # Deploying part of the database for equipment category 'Cables and wires'
    for table in (db.Mark, db.Amount, db.RangeVal, db.Cable):
        deploy_if_not_exist(table, DATA_DIR / 'cable_catalog' / table.__tablename__, clear)

    # Deploying part of the database for equipment category 'Current breaker devices'
    for table in (db.Device, db.CurrentNominal, db.CurrentBreaker):
        deploy_if_not_exist(table, DATA_DIR / 'current_breaker_catalog' / table.__tablename__, clear)

    # Deploying part of the database for equipment category 'Other resistances'
    deploy_if_not_exist(db.OtherContact, DATA_DIR / db.OtherContact.__tablename__, clear)


if __name__ == '__main__':
    install(clear=DB_TABLES_CLEAR_INSTALL)
