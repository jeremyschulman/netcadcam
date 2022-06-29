#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Union, List, Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.checks.check import Check

from .check_status import CheckStatus
from .check_result import CheckResult
from .check_exclusively import CheckExclusiveResult
from .check_measurement import CheckMeasurement, AnyMeasurementType

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "CheckResultsCollection",
    "CheckStatus",
    "CheckPassResult",
    "CheckFailResult",
    "CheckInfoLog",
    "CheckResult",
    "CheckSkipResult",
    "CheckFailMissingMembers",
    "CheckFailExtraMembers",
    "CheckFailFieldMismatch",
    "CheckFailNoExists",
    "CheckMeasurement",
    "CheckExclusiveResult",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#
#                         When a check passes ...
#
# -----------------------------------------------------------------------------


class CheckPassResult(CheckResult):
    status = CheckStatus.PASS
    field: Optional[str] = None

    @staticmethod
    def log_result(result: dict):
        """
        The log message to report to the User when results are processed.
        """
        expected = result["check"]["expected_results"]
        if (field := result.get("field")) and field in expected:
            expected = expected[field]
        return dict(expected=expected, measured=result["measurement"])


class NoCheck(Check):
    check_params = BaseModel()
    expected_results = BaseModel()

    def check_id(self) -> str:
        return "n/a"


class CheckSkipResult(CheckResult):
    status = CheckStatus.SKIP
    message: str
    check: Check = Field(default_factory=NoCheck)
    measurement: Optional[AnyMeasurementType] = None

    @staticmethod
    def log_result(result: dict):
        return result["message"]


# -----------------------------------------------------------------------------
#
#                         When a check fails ...
#
# -----------------------------------------------------------------------------


class CheckFailResult(CheckResult):
    status = CheckStatus.FAIL
    field: str
    error: Union[str, dict]

    @staticmethod
    def log_result(result: dict):
        return result.get("error") or result.get("logs")


class CheckFailNoExists(CheckFailResult):
    """The check failed since the measure item does not exist"""

    def __init__(self, device, check, **kwargs):
        kwargs.setdefault("field", "exists")
        kwargs.setdefault(
            "error",
            dict(
                error="missing",
                params=check.check_params.dict(),
                expected=check.expected_results.dict(),
            ),
        )

        super().__init__(device=device, check=check, **kwargs)


class CheckFailFieldMismatch(CheckFailResult):
    expected: Optional[AnyMeasurementType]
    error: Optional[Union[str, dict]]

    def __init__(self, device, check, field, measurement, expected=None, **kwargs):

        if expected is None:
            expected = getattr(check.expected_results, field)

        if "error" not in kwargs:
            kwargs["error"] = dict(
                error="mismatch", expected=expected, measured=measurement
            )

        super().__init__(
            device=device,
            check=check,
            field=field,
            measurement=measurement,
            **kwargs,
        )


class CheckFailExtraMembers(CheckFailResult):
    expected: List
    extras: List

    def __init__(self, device, check, expected, extras, **kwargs):
        if "error" not in kwargs:
            kwargs["error"] = dict(error="extras", expected=expected, extras=extras)

        super().__init__(
            device=device,
            check=check,
            expected=expected,
            extras=extras,
            **kwargs,
        )


class CheckFailMissingMembers(CheckFailResult):
    expected: List
    missing: List

    def __init__(self, device, check, expected, missing, **kwargs):
        if "error" not in kwargs:
            kwargs["error"] = dict(error="missing", expected=expected, missing=missing)

        super().__init__(
            device=device,
            check=check,
            expected=expected,
            missing=missing,
            **kwargs,
        )


# -----------------------------------------------------------------------------
#
#            When a check wants to provide additional information ...
#
# -----------------------------------------------------------------------------


class CheckInfoLog(CheckResult):
    status = CheckStatus.INFO
    field: Optional[str]

    @staticmethod
    def log_result(result: dict):
        return result["measurement"]


CheckResultsCollection = List[CheckResult]
