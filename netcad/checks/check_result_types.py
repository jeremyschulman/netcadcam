#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Union, List, Dict, Optional, Any
import enum

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import pydantic
from pydantic import validator, BaseModel, Field, Extra

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.helpers import StrEnum
from netcad.checks.check import Check

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
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

# !! order matters here, ensure bool is first
AnyMeasurementType = Union[bool, int, float, List, Dict, None, str]


# noinspection PyArgumentList
class CheckStatus(StrEnum):
    PASS = enum.auto()
    FAIL = enum.auto()
    INFO = enum.auto()
    SKIP = enum.auto()
    WARN = enum.auto()


class AllDeafultNone(pydantic.main.ModelMetaclass):
    def __new__(mcs, name, bases, namespaces, **kwargs):
        annotations = namespaces.get("__annotations__", {})
        for base in bases:
            annotations.update(base.__annotations__)

        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]

        namespaces["__annotations__"] = annotations
        return super().__new__(mcs, name, bases, namespaces, **kwargs)


class Measurement(BaseModel, extra=Extra.allow, metaclass=AllDeafultNone):
    pass


class CheckResult(BaseModel):
    status: CheckStatus = Field(CheckStatus.PASS)
    device: Device
    check: Check
    check_id: Optional[str]
    field: Optional[str]

    # The mesurement attribute is expected to be a BaseModel subclassed from
    # the Check expected_results BaseModel.  If there are no measurements it
    # means that the "thing" being checked by the DUT does not exist.

    measurement: Optional[Any] = Field(
        default_factory=str, description="The measurement from the DUT"
    )

    logs: List = Field(default_factory=list, description="Any logged by the DUT")

    # noinspection PyUnusedLocal
    @validator("check_id", always=True)
    def _save_tc_id(cls, value, values: dict):
        return values["check"].check_id()

    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def log_result(result: dict):
        raise NotImplementedError()

    def finalize(self):
        return _finalize_result(self)


def _finalize_result(result: CheckResult) -> CheckResult:

    check = result.check
    expd = check.expected_results
    msrd = result.measurement

    if not msrd:
        params = check.check_params
        result.status = CheckStatus.FAIL
        setattr(result, "field", "no-exists")
        result.logs.append(
            [
                "ERROR",
                "missing",
                dict(
                    params=params.dict() if params else None,
                    expected=check.expected_results.dict(),
                ),
            ]
        )
        return result

    # check to see if there are any field-mismatches
    mismatches = []

    for field in msrd.__fields__:

        m_field = getattr(msrd, field)

        if (e_field := getattr(expd, field, None)) is None:
            # extra data supplied by DUT
            result.logs.append(["INFO", field, m_field])
            continue

        if not (matched := (e_field == m_field)):
            mismatches.append(field)

        result.logs.append(
            [
                ["ERROR", "OK"][matched],
                field,
                {"expected": e_field, "measured": m_field},
            ]
        )

    if mismatches:
        setattr(result, "field", ", ".join(mismatches))
        result.status = CheckStatus.FAIL

    return result


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
