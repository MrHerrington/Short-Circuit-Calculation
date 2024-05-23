# -*- coding: utf-8 -*-
"""Module contains program configuration settings"""


from pathlib import Path
from decimal import Decimal


# Program settings

# Dirs paths
ROOT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = ROOT_DIR / 'config.py'
CREDENTIALS_DIR = ROOT_DIR / 'credentials.json'
DATA_DIR = ROOT_DIR / 'data'
GUI_DIR = ROOT_DIR / 'gui'
GRAPHS_DIR = GUI_DIR / 'resources' / 'graphs'

# Database settings
SQLITE_DB_NAME = 'electrical_product_catalog.db'
DB_EXISTING_CONNECTION = 'MySQL'
DB_TABLES_CLEAR_INSTALL = True
ENGINE_ECHO = False

# Calculations settings
SYSTEM_PHASES = 3
SYSTEM_VOLTAGE_IN_KILOVOLTS = Decimal('0.4')
CALCULATIONS_ACCURACY = 3
