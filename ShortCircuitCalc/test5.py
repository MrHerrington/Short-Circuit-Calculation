import logging
from decimal import Decimal, InvalidOperation
import re
import ast
from collections import namedtuple


logger = logging.getLogger(__name__)


class TypesManager:
    def __new__(cls, value, as_decimal=False, as_string=False, quoting=False):
        __new_val = TypesHandler(value, as_decimal, as_string, quoting)
        if __new_val.value is not None:
            return type(__new_val.value)(__new_val.value)
        else:
            return None


class TypesHandler:
    def __init__(self, value, as_decimal=False, as_string=False, quoting=False):
        self.__value = value
        self.__as_decimal = as_decimal
        self.__as_string = as_string
        self.__quoting = quoting

        # self.__types_converting()
        # self.__type_parser()
        self.__to_decimal()

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __types_converting(self):
        ConversionsList = namedtuple('ConversionsList', ('parse', 'decimal', 'string', 'quote'))
        __conversions_options = {

            ConversionsList(True, False, False, False): self.__type_parser(),
            ConversionsList(True, True, False, False): self.__type_parser().__to_decimal(),
            ConversionsList(True, False, True, False): self.__type_parser().__to_decimal(),
            ConversionsList(True, True, True, False): self.__type_parser().__to_decimal().__to_string(),

        }
        ################TODO######################

    def __type_parser(self):
        if isinstance(self.__value, str):
            match = re.search(r"Decimal\('([^']+)'\)", self.__value)
            if match:
                self.__value = Decimal(match.group(1))  # decimals parser
            else:
                try:
                    self.__value = ast.literal_eval(self.__value)  # others types parser
                except ValueError:
                    pass

        else:
            msg = f"Cannot parse non-string ({self.__value}, {type(self.__value)})."
            logger.error(msg)
            raise TypeError(msg) from None

        return self

    def __to_decimal(self):
        try:
            self.__value = Decimal(self.__value)
        except InvalidOperation:
            msg = f'Cannot convert ({self.__value}, {type(self.__value)}) to Decimal.'
            logger.error(msg)
            raise TypeError(msg) from None

        return self

    def __to_string(self):
        __type_to_string = {
            str: self.__value,
            Decimal: f"Decimal('{self.__value}')",
        }

        try:
            self.__value = __type_to_string[type(self.__value)]
        except KeyError:
            self.__value = str(self.__value)

        return self

    def __quoting(self):
        try:
            if "\'" in self.__value:
                self.__value = f'"{self.__value}"'
            else:
                self.__value = f"'{self.__value}'"
        except TypeError:
            msg = f"Cannot quoting ({self.__value}, {type(self.__value)}), use also 'to_string' option."
            logger.error(msg)
            raise TypeError(msg) from None

        return self

    def __repr__(self):
        return self.__value


a = [
    TypesManager("Decimal('0.1')"),
    TypesManager('0.1'),
    TypesManager('1'),
    TypesManager('fist'),
    TypesManager('True'),
    TypesManager('False'),
    TypesManager('finger'),
    TypesManager('None')
]

for i in a:
    print(i, type(i))
