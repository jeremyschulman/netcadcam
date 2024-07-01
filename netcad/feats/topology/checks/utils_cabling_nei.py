#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import re

# Some neighbor systems do not provide the full interface name. Therefore we
# will need to a "shortest name" match.

_re_short_ifname = re.compile(r"(\D+)(\d.*)")


def nei_hostname_match(expected: str, measured: str) -> bool:
    if expected.lower() == measured.lower():
        return True

    # the neighbor may be using a FQDN value, and the expected value is not.
    # Therefore we need to match only up to the expected hostname value.

    expd_len = len(expected)
    if (expected[:expd_len] == measured[:expd_len]) and measured[expd_len] == ".":
        return True

    # No match
    return False


def nei_interface_match(expected: str, measured: str) -> bool:
    # if match, then return True.

    if expected.lower() == measured.lower():
        return True

    # the neighbor may be using a "short" interface name; so try that next. if
    # no matching regex, then return False.

    if not (mo_msrd := _re_short_ifname.match(measured)):
        return False

    mo_expd = _re_short_ifname.match(expected)
    mo_expd_name, mo_expd_numbers = mo_expd.groups()
    mo_msrd_name, mo_msrd_numbers = mo_msrd.groups()

    # the "short" part of the name matches, and the "numbers" part of the name
    # exactly matches, then return True.

    if (expected[: len(mo_msrd_name)] == mo_msrd_name) and (
        mo_msrd_numbers == mo_expd_numbers
    ):
        return True

    # No match.
    return False
