# -*- coding: utf-8 -*-
"""
The package presents mixin classes, which extends the functionality of the declarative
base class 'Base'. Also, this package contains database installation tools and ORM
models of the database of various electrical devices, datasets objects for optimization
their CRUD methods and validation input data.

Mixin classes:
    BaseMixin: The class presented mixin for single source table ORM object.
    JoinedMixin: The class presented mixin for joined table ORM object.

Models:
    ###############
    # Main models #
    ###############
    PowerNominal: The class describes a table of transformer power nominals.
    VoltageNominal: The class describes a table of transformer voltage nominals.
    Scheme: The class describes a table of transformer vector group schemes.
    Transformer: The class describes a table of communication by transformers.

    Mark: The class describes a table of cable marking types.
    RangeVal: The class describes a table of cable ranges.
    Amount: The class describes a table of the number of conductive cores of cables.
    Cable: The class describes a table of communication by cables.

    Device: The class describes a table of switching devices.
    CurrentNominal: The class describes a table of the switching devices current nominals.
    CurrentBreaker: The class describes a table of the switching devices.

    OtherContact: The class describes a table of the others resistances.

    ###################################
    # Dataclasses for CRUD operations #
    ###################################
    InsertTrans: Dataclass provides dataset for 'Transformer.insert_joined_table()' method.
    UpdateTransOldSource, UpdateTransNewSource, UpdateTransRow: Dataclasses provide datasets
    for 'Transformer.update_joined_table()' method.
    DeleteTrans: Dataclass provides dataset for 'Transformer.delete_joined_table()' method.

    InsertCable: Dataclass provides dataset for 'Cable.insert_joined_table()' method.
    UpdateCableOldSource, UpdateCableNewSource, UpdateCableRow: Dataclasses provide datasets
    for 'Cable.update_joined_table()' method.
    DeleteCable: Dataclass provides dataset for 'Cable.delete_joined_table()' method.

    InsertContact: Dataclass provides dataset for 'OtherContact.insert_joined_table()' method.
    UpdateContactOldSource, UpdateContactNewSource, UpdateContactRow: Dataclasses provide datasets
    for 'OtherContact.update_joined_table()' method.
    DeleteContact: Dataclass provides dataset for 'OtherContact.delete_joined_table()' method.

    InsertResist: Dataclass provides dataset for 'OtherContact.insert_table()' method.
    UpdateResistOldSource, UpdateResistNewSource, UpdateResistRow: Dataclasses provide datasets
    for 'OtherContact.update_table()' method.
    DeleteResist: Dataclass provides dataset for 'OtherContact.delete_table()' method.

Installation tools:
    db_install: The function installs/reinstall the database fully or partially.

"""


from shortcircuitcalc.database.models import *
from shortcircuitcalc.database.install import *
