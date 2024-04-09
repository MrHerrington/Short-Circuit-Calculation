"""Module contains program configuration settings"""


from pathlib import Path
from decimal import Decimal


# Program settings
ROOT_DIR = Path(__file__).resolve().parent
DB_SECURITY_DIR = ROOT_DIR / 'db_security.json'
DATA_DIR = ROOT_DIR / 'data'
ENGINE_ECHO = False
DB_TABLES_CLEAR_INSTALL = True

# Calculations settings
SYSTEM_VOLTAGE_IN_KILOVOLTS = Decimal('0.4')
CALCULATIONS_ACCURACY = 3
