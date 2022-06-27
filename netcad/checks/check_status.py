#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import enum

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.text import Style

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.helpers import StrEnum


# noinspection PyArgumentList
class CheckStatusFlag(enum.IntFlag):
    """
    These check flags must be ordered from lowest to highest for sorting
    purposes.
    """

    PASS = enum.auto()
    INFO = enum.auto()
    SKIP = enum.auto()
    WARN = enum.auto()
    FAIL = enum.auto()

    def __str__(self):
        """when stringify, show the value name, for example "PASS" """
        return self.name


# noinspection PyArgumentList
class CheckStatus(StrEnum):
    PASS = enum.auto()
    FAIL = enum.auto()
    INFO = enum.auto()
    SKIP = enum.auto()
    WARN = enum.auto()

    def to_flag(self) -> CheckStatusFlag:
        return _map_status_to_flag[self]

    def to_style(self) -> Style:
        return _map_status_to_style[self]


_map_status_to_flag = {
    CheckStatus.PASS: CheckStatusFlag.PASS,
    CheckStatus.INFO: CheckStatusFlag.INFO,
    CheckStatus.FAIL: CheckStatusFlag.FAIL,
    CheckStatus.WARN: CheckStatusFlag.WARN,
    CheckStatus.SKIP: CheckStatusFlag.SKIP,
}

_map_status_to_style = {
    CheckStatus.PASS: Style(color="green"),
    CheckStatus.INFO: Style(color="blue"),
    CheckStatus.FAIL: Style(color="red"),
    CheckStatus.WARN: Style(color="yellow"),
    CheckStatus.SKIP: Style(color="magenta"),
}
