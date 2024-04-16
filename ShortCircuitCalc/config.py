# -*- coding: utf-8 -*-
"""Module contains program configuration settings"""


from pathlib import Path
from decimal import Decimal


# Program settings
ROOT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = ROOT_DIR / 'config.py'
CREDENTIALS_DIR = ROOT_DIR / 'credentials.json'
DATA_DIR = ROOT_DIR / 'data'
ENGINE_ECHO = False
DB_EXISTING_CONNECTION = 'MySQL'
DB_TABLES_CLEAR_INSTALL = False
SQLITE_DB_NAME = 'electrical_product_catalog.db'

# Calculations settings
SYSTEM_VOLTAGE_IN_KILOVOLTS = Decimal('0.4')
CALCULATIONS_ACCURACY = 3
