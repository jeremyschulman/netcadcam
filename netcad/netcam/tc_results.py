from typing import Any

from pydantic.dataclasses import dataclass
from netcad.testing_services.test_case import TestCase

__all__ = ["TestCasePass", "TestCaseFailed", "TestCaseInfo", "TestCaseResults"]


@dataclass
class TestCaseResults:
    device: Any
    test_case: TestCase
    field: str
    measurement: Any


@dataclass
class TestCasePass(TestCaseResults):
    pass


@dataclass
class TestCaseFailed(TestCaseResults):
    error: str


@dataclass
class TestCaseInfo(TestCaseResults):
    pass
