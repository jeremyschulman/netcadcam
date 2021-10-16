from typing import List
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

    #
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
