# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List
from itertools import groupby
from enum import Enum

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["range_string", "StrEnum", "HashableModel"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


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

    def _generate_next_value_(name, start, count, last_values):  # noqa
        return name


def range_string(numbers: List[int]) -> str:

    # if the list is empty, return an empty string
    if not len(numbers):
        return ""

    values = list()
    for _, members in groupby(enumerate(numbers), key=lambda ele: ele[0] - ele[1]):
        *start, (_, last) = members
        if not start:
            values.append(str(last))
        else:
            sep = "," if len(start) == 1 else "-"
            values.append(f"{start[0][1]}{sep}{last}")

    return ",".join(values)


class HashableModel(BaseModel):
    """
    A pydantic quali-basemodel that allows for hashing.  This allows specific
    instances to be used as keys in dictionaries, added to sets, and other
    hashable applications.

    References
    ----------
    https://github.com/samuelcolvin/pydantic/issues/1303
    """

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))
