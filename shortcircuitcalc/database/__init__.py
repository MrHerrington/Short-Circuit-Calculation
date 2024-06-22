# -*- coding: utf-8 -*-
"""
The package presents mixin classes, which extends the functionality of the declarative
base class 'Base'. Also, this package contains database installation tools and ORM
models of the database of various electrical devices, datasets objects for optimization
their CRUD methods and validation input data.

Modules:
    - install: Module contains database installation tools.
    - mixins: Module contains mixin classes, which extends the functionality 'Base' class.
    - models: Module contains tables models of the database and dataclasses for CRUD operations.

"""


from shortcircuitcalc.database.models import *
from shortcircuitcalc.database.install import *
