import typing as ty
from dataclasses import dataclass, field, asdict


class Validator:
    """The class for validating the input data.

    The class for validating the input data in accordance with
    the type annotations specified when creating the dataclasses.

    Samples:
        @dataclass
        class Person:
            age: float = field(default=Validator())
            ---: ...

        print(Person('10').age) -> 10.0
        print(type(Person('10').age)) -> <class 'float'>

    """

    def __init__(self, default=None, prefer_default: bool = False) -> None:
        self._default = default
        self._prefer_default = prefer_default
        self._saved_value = None

    def __set_name__(self, owner: ty.Any, name: ty.Any) -> None:
        self._public_name = name
        self._private_name = '_' + name

    def __get__(self, obj: ty.Any, owner: ty.Any) -> ty.Any:
        type_error_msg = (f"[GETTER] The type of the attribute '{type(obj).__name__}.{self._public_name}' "
                          f"must be '{ty.get_type_hints(obj)[self._public_name].__name__}', "
                          f"now '{type(self._saved_value).__name__}'.")

        self._saved_value = getattr(obj, self._private_name)

        if isinstance(self._saved_value, ty.get_type_hints(obj)[self._public_name]):
            return self._saved_value
        else:
            print(type_error_msg)

    def __set__(self, obj: ty.Any, value: ty.Any) -> None:
        # https://stackoverflow.com/questions/67612451/combining-a-descriptor-class-with-dataclass-and-field
        # Next in Validator.__set__, when the arg argument is not provided to the
        # constructor, the value argument will actually be the instance of the
        # Validator class. So we need to change the guard to see if value is self:
        type_error_msg = (f"[SETTER] The type of the attribute '{type(obj).__name__}.{self._public_name}' "
                          f"must be '{ty.get_type_hints(obj)[self._public_name].__name__}', "
                          f"now '{type(self._saved_value).__name__}'.")
        empty_str_error_msg = (f"[SETTER] Attribute '{type(obj).__name__}.{self._public_name}' "
                               f'must be non empty string.')

        def __set_valid_arg():
            if isinstance(self._default, str) and self._default or \
                    not (isinstance(self._default, str)) and self._default is not None:
                return ty.get_type_hints(obj)[self._public_name](self._default)
            else:
                if isinstance(self._default, str) and not self._default:
                    print(empty_str_error_msg)

        def __set_obj_arg(arg):
            if isinstance(arg, str) and arg or \
                    not (isinstance(arg, str)) and arg is not None:
                return ty.get_type_hints(obj)[self._public_name](arg)
            else:
                if isinstance(arg, str) and not arg:
                    print(empty_str_error_msg)

        try:
            if value is self:
                value = __set_valid_arg()

            else:
                if self._prefer_default or not value:
                    value = __set_valid_arg()
                else:
                    value = __set_obj_arg(value)

        except (Exception,):
            print(type_error_msg)
            # raise

        setattr(obj, self._private_name, value)

    def __str__(self) -> str:
        return f'{self._saved_value}'


@dataclass
class Target:
    resistance: float = field(default=Validator(0))
    reactance: int = field(default=Validator())


t = Target()
print(t)
