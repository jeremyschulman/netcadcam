# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Union, List, Dict, Optional
import enum

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from pydantic import validator, BaseModel, Field

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
    "CollectionTestResults",
    "TestCaseStatus",
    "PassTestCase",
    "FailTestCase",
    "InfoTestCase",
    "ResultsTestCase",
    "SkipTestCases",
    "FailMissingMembersResult",
    "FailExtraMembersResult",
    "FailFieldMismatchResult",
    "FailNoExistsResult",
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
    SKIP = enum.auto()


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

    @staticmethod
    def log_result(result: dict):
        raise NotImplementedError()


# -----------------------------------------------------------------------------
#
#                         When a testcase passes ...
#
# -----------------------------------------------------------------------------


class PassTestCase(ResultsTestCase):
    status = TestCaseStatus.PASS
    field: Optional[str]

    @staticmethod
    def log_result(result: dict):
        """
        The log message to report to the User when results are processed.
        """
        expected = result["test_case"]["expected_results"]
        if (field := result.get("field")) and field in expected:
            expected = expected[field]
        return dict(expected=expected, measured=result["measurement"])


class NoneTestCase(TestCase):
    test_params = BaseModel()
    expected_results = BaseModel()

    def test_case_id(self) -> str:
        return "n/a"


class SkipTestCases(ResultsTestCase):
    status = TestCaseStatus.SKIP
    message: str
    test_case: TestCase = Field(default_factory=NoneTestCase)
    measurement: Optional[AnyMeasurementType] = None

    @staticmethod
    def log_result(result: dict):
        return result["message"]


# -----------------------------------------------------------------------------
#
#                         When a testcase fails ...
#
# -----------------------------------------------------------------------------


class FailTestCase(ResultsTestCase):
    status = TestCaseStatus.FAIL
    field: str
    error: Union[str, dict]

    @staticmethod
    def log_result(result: dict):
        return result["error"]


class FailNoExistsResult(FailTestCase):
    """The test case failed since the measure item does not exist"""

    def __init__(self, device, test_case, **kwargs):
        kwargs.setdefault("field", "exists")
        kwargs.setdefault(
            "error", dict(error="missing", expected=test_case.expected_results.dict())
        )

        super().__init__(device=device, test_case=test_case, **kwargs)


class FailFieldMismatchResult(FailTestCase):
    expected: Optional[AnyMeasurementType]
    error: Optional[Union[str, dict]]

    def __init__(self, device, test_case, field, measurement, expected=None, **kwargs):

        if expected is None:
            expected = getattr(test_case.expected_results, field)

        if "error" not in kwargs:
            kwargs["error"] = dict(
                error="mismatch", expected=expected, measured=measurement
            )

        super().__init__(
            device=device,
            test_case=test_case,
            field=field,
            measurement=measurement,
            **kwargs,
        )


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
            **kwargs,
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
            **kwargs,
        )


# -----------------------------------------------------------------------------
#
#            When a testcase wants to provide additional information ...
#
# -----------------------------------------------------------------------------


class InfoTestCase(ResultsTestCase):
    status = TestCaseStatus.INFO
    field: Optional[str]

    @staticmethod
    def log_result(result: dict):
        return result["measurement"]


CollectionTestResults = List[ResultsTestCase]
