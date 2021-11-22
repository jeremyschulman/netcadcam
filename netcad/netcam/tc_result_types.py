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


class FailNoExistsTestCase(FailTestCase):
    """The test case failed since the measure item does not exist"""

    def __init__(self, device, test_case, **kwargs):
        kwargs.setdefault("error", dict(error="missing", field="exists"))
        kwargs.setdefault("field", "exists")

        super().__init__(device=device, test_case=test_case, **kwargs)


class FailFieldMismatchTestCase(FailTestCase):
    error: Optional[Union[str, dict]]

    @validator("error", always=True)
    def _form_errmsg(cls, value, values: dict):
        # if the Caller provided a value to override the default, then use it
        # as-is. otherwise form the default error message.

        if value:
            return value

        field = values["field"]
        exp_val = getattr(values["test_case"].expected_results, field)
        msr_val = values["measurement"]
        return dict(error="mismatch", expected=exp_val, measured=msr_val)


# -----------------------------------------------------------------------------
#
#            When a testcase wants to provide additional information ...
#
# -----------------------------------------------------------------------------


class InfoTestCase(ResultsTestCase):
    status = TestCaseStatus.INFO
    field: Optional[str]
