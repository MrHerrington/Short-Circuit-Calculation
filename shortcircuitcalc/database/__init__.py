# -*- coding: utf-8 -*-
"""
The package presents mixin classes, which extends the functionality of the declarative
base class 'Base'. Also, this package contains database installation tools and ORM
models of the database of various electrical devices, datasets objects for optimization
their CRUD methods and validation input data. This module contains classes and dataclasses
for various electrical elements such as transformers, cables and contacts, for programmatically
inputting data related to these categories.

Modules:
    - install: Module contains database installation tools.
    - mixins: Module contains mixin classes, which extends the functionality 'Base' class.
    - models: Module contains tables models of the database and dataclasses for CRUD operations.
    - units: Module contains classes and dataclasses for various electrical elements.

"""


from shortcircuitcalc.database.units import *
from shortcircuitcalc.database.models import *
from shortcircuitcalc.database.install import *
from shortcircuitcalc.database.mixins import BT
