from typing import List
from itertools import groupby


def vlan_range_string(vlan_ids: List[int]) -> str:
    """
    Given a *sorted* list of numbers (VLAN-IDs), return a string that
    converts consecuitve numbers into comma separated ranges.  For example:
        [1,2,3,4,5,7,10,11,12] -> "1-5,7,10-12"

    Parameters
    ----------
    vlan_ids: List[int]
        The *sorted* list of vlan ID numbers.

    Returns
    -------
    The string as described.
    """

    range_strings = list()

    for _, num_gen in groupby(enumerate(vlan_ids), key=lambda x: x[0] - x[1]):
        num_list = tuple(num_gen)
        first, last = num_list[0], num_list[-1]
        range_strings.append(
            str(first[1]) if first is last else f"{first[1]}-{last[1]}"
        )

    return ",".join(range_strings)
