from typing import List, Optional, Any
from itertools import groupby
from enum import Enum


class StrEnum(str, Enum):
    """
    StrEnum allows for the use of enum.auto() to define the value the string of
    the name.  For example:

        class Foo(StrEnum):
            this = auto()
            that = auto()

        Then Foo.this will serialize to the string "this".  Likewise a call to
        Foo("this") will deserialize to Foo.this.
    """

    def _generate_next_value_(name, start, count, last_values):
        return name


def range_string(numbers: List[int]) -> str:
    """
    Given a *sorted* list of numbers (VLAN-IDs), return a string that
    converts consecuitve numbers into comma separated ranges.  For example:
        [1,2,3,4,5,7,10,11,12] -> "1-5,7,10-12"

    Parameters
    ----------
    numbers: List[int]
        The *sorted* list of vlan ID numbers.

    Returns
    -------
    The string as described.
    """

    range_strings = list()

    for _, num_gen in groupby(enumerate(numbers), key=lambda x: x[0] - x[1]):
        num_list = tuple(num_gen)
        first, last = num_list[0], num_list[-1]
        range_strings.append(
            str(first[1]) if first is last else f"{first[1]}-{last[1]}"
        )

    return ",".join(range_strings)


class Registry(object):
    """
    Registry mechanism that allows instances of the given class, generally
    called by the class __init__ method.  See the Device class for example.
    """

    __registry = None

    def __init_subclass__(cls, **kwargs):
        """each subclass will be given a unique registry dictionary"""
        cls.__registry = dict()

    @classmethod
    def registry_add(cls, name, obj):
        """add the named object to the registry"""
        cls.__registry[name] = obj

    @classmethod
    def registry_get(cls, name: str) -> Optional[Any]:
        """
        Return the registered item designative by 'name', or None if not found.
        This search will start with the class used in by the Caller, and if not
        found there, will check any subclassed registries.

        Parameters
        ----------
        name: str
            The registered name.

        Returns
        -------
        The object that was registered by the given name if found.
        None if not found.
        """
        return next(
            (
                # return the object given by name
                each_cls.__registry.get(name)
                # check _this_ class, and then any subclasses.
                for each_cls in (cls, *cls.__subclasses__())
                # if the name is in the registry then return this object
                if name in each_cls.__registry
            ),
            # Nothing found, so return None to Caller
            None,
        )

    @classmethod
    def registry_list(cls, subclasses=True) -> List[str]:
        """
        Return a list of the named objects in the registry.  By default all
        items including subclasses of the registry are returned.  If the Caller
        wants only _this class_ registry, then set subclass=False.

        Parameters
        ----------
        subclasses: bool
            Determines whether or not to include subclassed registries.

        Returns
        -------
        List of the registered names.
        """
        if not subclasses:
            return list(cls.__registry)

        return [
            name
            for each_cls in (cls, *cls.__subclasses__())
            for name in each_cls.__registry.keys()
        ]
