#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, List, TypeVar, Generic
from typing import Callable

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import RootModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .check import Check
from .check_status import CheckStatus
from .check_result import CheckResult

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["CheckExclusiveResult", "CheckExclusiveList", "CheckExclusiveListGeneric"]


DataT = TypeVar("DataT")
CheckT = TypeVar("CheckT", bound=Check)


class CheckExclusiveListGeneric(RootModel[DataT]):
    root: List[DataT]


class CheckExclusiveList(CheckExclusiveListGeneric[str]):
    pass


class CheckExclusiveResult(CheckResult[CheckT], Generic[CheckT]):
    """
    This generic sublcass of CheckResult is used for the purposes of
    exclusively checking "lists of things", which are generally list of
    strings.  But could be list of ints, which is why the DataT is a generic,
    and the CheckT represents the generic check-type this result is bound to.

    Notes
    -----
    The use of Generic[CheckT] in the class declaration is required, at least
    at this time, as an artifact of the pydantic library implementation, and
    discussed on this GitHub issue:
    https://github.com/samuelcolvin/pydantic/issues/2380#issuecomment-782330241
    """

    def measure(
        self, sort_key: Optional[Callable] = None, on_extra: CheckStatus = None
    ):
        check = self.check
        msrd = self.measurement
        expd = check.expected_results

        msrd_set = set(msrd.root)
        expd_set = set(expd.root)

        if missing_set := expd_set - msrd_set:
            items = sorted(missing_set, key=sort_key)
            self.logs.FAIL("missing", items)
            self.status = CheckStatus.FAIL

        if extra_set := (msrd_set - expd_set):
            items = sorted(extra_set, key=sort_key)

            if not on_extra:
                self.logs.FAIL("extra", items)
                self.status = CheckStatus.FAIL

            else:
                getattr(self.logs, on_extra)("extra", items)
                self.status = on_extra

        return self
