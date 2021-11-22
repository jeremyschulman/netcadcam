# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Union, List, Dict, Optional
import enum

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import validator, BaseModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.helpers import StrEnum
from netcad.testing_services.test_case import TestCase

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "TestCaseStatus",
    "PassTestCase",
    "FailTestCase",
    "InfoTestCase",
    "ResultsTestCase",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

# !! order matters here, ensure bool is first
AnyMeasurementType = Union[bool, int, float, List, Dict, None, str]


class TestCaseStatus(StrEnum):
    PASS = enum.auto()
    FAIL = enum.auto()
    INFO = enum.auto()


class ResultsTestCase(BaseModel):
    status: TestCaseStatus
    device: Device
    test_case: TestCase
    test_case_id: Optional[str]
    measurement: AnyMeasurementType

    # noinspection PyUnusedLocal
    @validator("test_case_id", always=True)
    def _save_tc_id(cls, value, values: dict):
        return values["test_case"].test_case_id()

    class Config:
        arbitrary_types_allowed = True


# -----------------------------------------------------------------------------
#
#                         When a testcase passes ...
#
# -----------------------------------------------------------------------------


class PassTestCase(ResultsTestCase):
    status = TestCaseStatus.PASS
    field: Optional[str]


# -----------------------------------------------------------------------------
#
#                         When a testcase fails ...
#
# -----------------------------------------------------------------------------


class FailTestCase(ResultsTestCase):
    status = TestCaseStatus.FAIL
    field: str
    error: Union[str, dict]


class FailNoExistsResult(FailTestCase):
    """The test case failed since the measure item does not exist"""

    def __init__(self, device, test_case, **kwargs):
        kwargs.setdefault("error", dict(error="missing", field="exists"))
        kwargs.setdefault("field", "exists")

        super().__init__(device=device, test_case=test_case, **kwargs)


class FailFieldMismatchResult(FailTestCase):
    expected: Optional[AnyMeasurementType]
    error: Optional[Union[str, dict]]

    def __init__(self, **kwargs):

        if "expected" not in kwargs:
            kwargs["expected"] = getattr(
                kwargs["test_case"].expected_results, kwargs["field"]
            )

        if "error" not in kwargs:
            kwargs["error"] = dict(
                error="mismatch",
                expected=kwargs["expected"],
                measured=kwargs["measurement"],
            )

        super().__init__(**kwargs)


class FailExtraMembersResult(FailTestCase):
    expected: List
    extras: List

    def __init__(self, device, test_case, expected, extras, **kwargs):
        if "error" not in kwargs:
            kwargs["error"] = dict(error="extras", expected=expected, extras=extras)

        super().__init__(
            device=device,
            test_case=test_case,
            expected=expected,
            extras=extras,
            **kwargs
        )


class FailMissingMembersResult(FailTestCase):
    expected: List
    missing: List

    def __init__(self, device, test_case, expected, missing, **kwargs):
        if "error" not in kwargs:
            kwargs["error"] = dict(error="missing", expected=expected, missing=missing)

        super().__init__(
            device=device,
            test_case=test_case,
            expected=expected,
            missing=missing,
            **kwargs
        )


# -----------------------------------------------------------------------------
#
#            When a testcase wants to provide additional information ...
#
# -----------------------------------------------------------------------------


class InfoTestCase(ResultsTestCase):
    status = TestCaseStatus.INFO
    field: Optional[str]
