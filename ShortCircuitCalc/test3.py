import logging
from ShortCircuitCalc.database import *


logging.basicConfig(level=logging.INFO)

handler = logging.FileHandler(f"{__name__}.log", mode='w')
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)


Cable.show_table(False)
