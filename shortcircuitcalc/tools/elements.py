# -*- coding: utf-8 -*-
"""
This module contains classes for electrical system calculations.

Classes:
    - ElemChain: The class describes the chain of elements.
    - ChainsSystem: The class describes system of chains of elements.

"""


import logging
import math
import re
import typing as ty

from decimal import Decimal
from functools import reduce

from shortcircuitcalc.tools.tools import config_manager
# Need for global space of units
from shortcircuitcalc.database.units import *  # noqa


__all__ = ('ElemChain', 'ChainsSystem')


logger = logging.getLogger(__name__)


class ElemChain(ty.Sequence, ty.Mapping):
    # noinspection PyUnresolvedReferences, PyTypeChecker
    """
    The class describes the chain of elements.

    Attributes:
        obj (Union[Sequence, Mapping]): The chain of elements.

    Public properties:
        - three_phase_current_short_circuit: The method calculates the three-phase current during a short circuit.
        - two_phase_current_short_circuit: The method calculates the two-phase current during a short circuit.
        - one_phase_current_short_circuit: The method calculates the one-phase current during a short circuit.

    Samples data input as sequence:

    .. code-block:: python

        >> ElemChain((QS(63), QF(25), Line()))
        QS(63) -> QF(25) -> Line()
        >>
        >> ElemChain([QS(63), W('ВВГ', 3, 2.5, 50)])
        QS(63) -> W('ВВГ', 3, 2.5, 50)

    Samples data input as mapping:

    .. code-block:: python

        >> ElemChain({'QS1': QS(63), 'QF1': QF(25), 'R1': Line()})
        QS1: QS(63) -> QF1: QF(25) -> R1: Line()
        >>
        >> ElemChain({'QS1': QS(63), 'W1': W('ВВГ', 3, 2.5, 50)})
        QS1: QS(63) -> W1: W('ВВГ', 3, 2.5, 50)

    """
    def __init__(self, obj: ty.Union[ty.Sequence, ty.Mapping]) -> None:
        self._obj = obj

    @property
    def obj(self) -> ty.Union[ty.Sequence, ty.Mapping]:
        return self._obj

    @property
    def three_phase_current_short_circuit(self) -> Decimal:
        """
        Calculates the three-phase current during a short circuit.

        Returns:
            Decimal: The calculated three-phase current during a short circuit.

        .. math::
            I_{k^{(3)}} = \\frac{U}{\\sqrt{3} * z_{^{(3)}}}

        :math:`U` - voltage value,
        :math:`z_{^{(3)}}` - three-phase summary resistance.

        """
        return round(
            (
                config_manager('SYSTEM_VOLTAGE_IN_KILOVOLTS') / Decimal(math.sqrt(3)) /
                self.__three_phase_summary_resistance()
            ),
            config_manager('CALCULATIONS_ACCURACY')
        )

    @property
    def two_phase_current_short_circuit(self) -> Decimal:
        """
        Calculates the two-phase current during a short circuit.

        Returns:
            Decimal: The calculated two-phase current during a short circuit.

        .. math::
            I_{k^{(2)}} = \\frac{\\sqrt{3} * I_{k^{(3)}}}{2}

        :math:`I_{k^{(3)}}` - three-phase current during a short circuit.

        """
        return round(
            (
                Decimal(math.sqrt(3)) / 2 * self.three_phase_current_short_circuit
            ),
            config_manager('CALCULATIONS_ACCURACY')
        )

    @property
    def one_phase_current_short_circuit(self) -> Decimal:
        """
        Calculates the one-phase current during a short circuit.

        Returns:
            Decimal: The calculated one-phase current during a short circuit.

        .. math::
            I_{k^{(1)}} = \\frac{\\sqrt{3} * U}{z_{^{(1)}}}

        :math:`U` - voltage value,
        :math:`I_{k^{(1)}}` - one-phase current during a short circuit.

        """
        return round(
            (
                Decimal(math.sqrt(3)) * config_manager('SYSTEM_VOLTAGE_IN_KILOVOLTS') /
                self.__one_phase_summary_resistance()
            ),
            config_manager('CALCULATIONS_ACCURACY')
        )

    def __three_phase_summary_resistance(self) -> Decimal:
        """
        Service function, calculates three-phase summary resistance.

        Returns:
            single Decimal value.

        .. math::
            z_{^{(3)}} = \\sqrt{r_{1\\sum_{}^{2}} + x_{1\\sum_{}^{2}}}

        :math:`r_1` - resistance value resistance_r1,
        :math:`x_1` - reactance value reactance_x1.

        """
        def __summary_resistance(obj: ty.Union[ty.Sequence, dict.values]) -> Decimal:
            """
            Service function, calculates summary resistance.

            Args:
                obj (Union[Sequence, Mapping]): The chain of elements.

            Returns:
                summary resistance as single Decimal value.

            """
            return Decimal(
                math.sqrt(
                    math.pow(
                        reduce(
                            lambda x, y: x + y, (i.resistance_r1 for i in obj)
                        ), 2
                    ) +
                    math.pow(
                        reduce(
                            lambda x, y: x + y, (i.reactance_x1 for i in obj)
                        ), 2
                    )
                )
            )

        if isinstance(self.obj, ty.Sequence):
            return __summary_resistance(self.obj)

        if isinstance(self.obj, ty.Mapping):
            return __summary_resistance(self.obj.values())

    def __one_phase_summary_resistance(self) -> Decimal:
        """
        Service function, calculates one-phase summary resistance.

        Returns:
            single Decimal value.

        .. math::
            z_{^{(1)}} = \\sqrt{{(2r_{1\\sum_{}} + r_{0\\sum_{}})}^{2} + {(2x_{1\\sum_{}} + x_{0\\sum_{}})}^{2}}

        :math:`r_1` - resistance value resistance_r1,
        :math:`r_0` - resistance value resistance_r0,
        :math:`x_1` - reactance value reactance_x1,
        :math:`x_0` - reactance value reactance_x0.

        """
        def __summary_resistance(obj: ty.Union[ty.Sequence, dict.values]) -> Decimal:
            """
            Service function, calculates summary resistance.

            Args:
                obj (Union[Sequence, Mapping]): The chain of elements.

            Returns:
                summary resistance as single Decimal value.

            """
            return Decimal(
                math.sqrt(
                    math.pow(
                        2 * reduce(
                            lambda x, y: x + y, (i.resistance_r1 for i in obj)
                        ) +
                        reduce(
                            lambda x, y: x + y, (i.resistance_r0 for i in obj)
                        ), 2
                    ) +
                    math.pow(
                        2 * reduce(
                            lambda x, y: x + y, (i.reactance_x1 for i in obj)
                        ) +
                        reduce(
                            lambda x, y: x + y, (i.reactance_x0 for i in obj)
                        ), 2
                    )
                )
            )

        if isinstance(self.obj, ty.Sequence):
            return __summary_resistance(self.obj)

        if isinstance(self.obj, ty.Mapping):
            return __summary_resistance(self.obj.values())

    def __getitem__(self, key):
        if isinstance(self.obj, ty.Sequence):
            if isinstance(key, slice):
                return ElemChain(self.obj[key])
            else:
                return self.obj[key]

        if isinstance(self.obj, ty.Mapping):
            if isinstance(key, slice):
                return ElemChain(dict(tuple(self.obj.items())[key]))
            else:
                return dict((tuple(self.obj.items())[key],))

    def __len__(self):
        return len(self.obj)

    def __str__(self):
        if isinstance(self.obj, ty.Sequence):
            return f"{' -> '.join(map(str, self.obj))}"

        if isinstance(self.obj, ty.Mapping):
            return f"{' -> '.join('%s: %s' % (key, value) for key, value in zip(self.obj.keys(), self.obj.values()))}"

    def __repr__(self):
        return f"ElemChain{self.obj}"


class ChainsSystem(ty.Iterable):
    # noinspection PyUnresolvedReferences
    """
    The class describes system of chains of elements.

    The class describes system of chains of elements. If input argument has
    string type, it will be parsed to the system of chains of elements.

    Attributes:
        obj (Union[Iterable, str]): The system of chains of elements.

    Samples:

    .. code-block:: python

        >> ChainsSystem([
               ElemChain([T(160, 'У/Ун-0'), QS(160), QF(160)]),
               ElemChain([QF(25)])
           ])
        [ChainsSystem of 2 chains / 4 elements]
        >>
        >> ChainsSystem([
               ElemChain({'T1': T(160, 'У/Ун-0'), 'QS1': QS(160), 'QF1': QF(160)}),
               ElemChain([QF(25)])
           ])
        [ChainsSystem of 2 chains / 4 elements]
        >>
        >> ChainsSystem(
               "T(160, 'У/Ун-0'), QS(160), QF(160), Line(), QF(25), W('ВВГ', 3, 4, 20), Line(), Arc();"
               "TCH: T(160, 'У/Ун-0'), QF3: QF(100), R1: Line(), QF2: QF(25), W1: W('ВВГ', 3, 4, 20)"
           )
        [ChainsSystem of 2 chains / 13 elements]

    """
    def __init__(self, obj):
        self.obj = obj
        if isinstance(self.obj, str):
            self.__parse_obj__()

    def __parse_obj__(self):
        """
        Service method parse obj argument into ElemChain objects if it has string type.

        """
        # regex patterns
        delimiter_pattern = r';\s*(?![^(]*\))'
        iterable_pattern = r'(?P<type>\w+)\((?P<args>.*?)\)'
        mapping_pattern = r'((?P<name>\w+):)\s*(?P<type>\w+)\((?P<args>.*?)\)'

        # split chains
        chains = re.split(delimiter_pattern, self.obj)

        for n in range(len(chains)):
            chain = tuple(re.finditer(mapping_pattern, chains[n]))
            if chain:
                chains[n] = ElemChain(
                    dict(
                        map(
                            lambda elem: (
                                elem.group('name'), globals()[elem.group('type')](
                                    *[x.strip('\'\"') for x in elem.group('args').split(', ')]
                                )
                            ), chain
                        )
                    )
                )
            else:
                chain = tuple(re.finditer(iterable_pattern, chains[n]))
                chains[n] = ElemChain(
                    tuple(
                        map(
                            lambda elem: globals()[elem.group('type')](
                                *[x.strip('\'\"') for x in elem.group('args').split(', ')]
                            ),
                            chain
                        )
                    )
                )
        self.obj = chains

    def __iter__(self):
        return iter(self.obj)

    def __len__(self):
        return len(self.obj)

    def __str__(self):
        return f"[ChainsSystem of {len(self.obj)} chains / {sum(map(len, self.obj))} elements]"

    def __repr__(self):
        return f'ChainsSystem{self.obj}'
