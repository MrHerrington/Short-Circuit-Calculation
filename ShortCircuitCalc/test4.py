import logging
from shortcircuitcalc.database import *
import shortcircuitcalc.tools as tools


# logging.basicConfig(level=logging.INFO)
#
# handler = logging.FileHandler(f"{__name__}.log", mode='w')
# formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
# handler.setFormatter(formatter)
# logging.getLogger().addHandler(handler)


# Cable.show_table()


a = getattr(tools, 'T')('1600', 'У/Ун-0')
print(a)
