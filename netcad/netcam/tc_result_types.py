# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Union, List, Dict, Optional

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import validator, BaseModel

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.testing_services.test_case import TestCase

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["TestCasePass", "TestCaseFailed", "TestCaseInfo", "TestCaseResults"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

# !! order matters here, ensure bool is first
AnyMeasurementType = Union[bool, str, float, int, List, Dict, None]


class TestCaseResults(BaseModel):

    device: Device
    test_case: TestCase
    field: str
    measurement: AnyMeasurementType

    class Config:
        arbitrary_types_allowed = True


# -----------------------------------------------------------------------------
#
#                         When a testcase passes ...
#
# -----------------------------------------------------------------------------


class TestCasePass(TestCaseResults):
    pass


# -----------------------------------------------------------------------------
#
#                         When a testcase fails ...
#
# -----------------------------------------------------------------------------


class TestCaseFailed(TestCaseResults):
    error: str


class TestCaseFailedOnField(TestCaseFailed):
    error: Optional[str]

    @validator("error", always=True)
    def _form_errmsg(cls, value, values: dict):
        # if the Caller provided a value to override the default, then use it
        # as-is. otherwise form the default error message.

        if value:
            return value

        field = values["field"]
        exp_val = getattr(values["test_case"].expected_results, field)
        msr_val = values["measurement"]
        return f"Mismatch: field={field}: expected={exp_val}, measured={msr_val}"


# -----------------------------------------------------------------------------
#
#            When a testcase wants to provide additional information ...
#
# -----------------------------------------------------------------------------


class TestCaseInfo(TestCaseResults):
    pass
