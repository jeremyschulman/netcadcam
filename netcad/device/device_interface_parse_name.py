#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple, Callable
import re
from dataclasses import dataclass

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


_re_find_numbers = re.compile(r"\d+")
_re_find_words = re.compile(r"\b([a-z]+)\b", re.IGNORECASE)

# short-name is the first two characters of the name, followed by the remaining
# interface numbers.  For example, "Ethernet49/1" turns into "Et49/1"

_re_short_name = re.compile(r"(\D+)(\d.*)")


@dataclass(frozen=True)
class DeviceInterfaceNameParsed:
    numbers: Tuple[int]
    short_name: str
    sort_key: Tuple


ParserFunction = Callable[[str], DeviceInterfaceNameParsed]


def default_interface_parse_name(name: str):

    mo_has_numbers = _re_find_numbers.findall(name)

    # for interface names without any numbers like "mgmt"

    if not mo_has_numbers:
        return DeviceInterfaceNameParsed(
            numbers=(0,), short_name=name, sort_key=(name,)
        )

    port_numbers = tuple(map(int, mo_has_numbers))
    mo_short_name = _re_short_name.match(name)
    prefix, numstr = mo_short_name.groups()
    short_prefix = prefix[0 : min(2, len(prefix))].lower()

    return DeviceInterfaceNameParsed(
        numbers=port_numbers,
        short_name=f"{short_prefix}{numstr}",
        sort_key=(short_prefix, *port_numbers),
    )
