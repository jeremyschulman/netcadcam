#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional
from typing import Callable

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------


from .check_status import CheckStatus
from .check_result import CheckResult


class CheckExclusiveResult(CheckResult):
    def finalize(self, sort_key: Optional[Callable] = None):
        check = self.check
        msrd = self.measurement
        expd = check.expected_results

        msrd_set = set(msrd.__root__)
        expd_set = set(expd.__root__)  # noqa

        if missing_set := expd_set - msrd_set:
            items = sorted(missing_set, key=sort_key)
            self.logs.append(["ERROR", "missing", items])

        if extra_set := (msrd_set - expd_set):
            items = sorted(extra_set, key=sort_key)
            self.logs.append(["ERROR", "extra", items])

        if missing_set or extra_set:
            self.status = CheckStatus.FAIL

        return self
