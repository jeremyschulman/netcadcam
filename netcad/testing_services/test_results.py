from typing import Any

from pydantic.dataclasses import dataclass
from .test_case import TestCase


@dataclass
class TestCaseResults:
    device: Any
    test_case: TestCase
    measurement: Any


@dataclass
class TestCasePass(TestCaseResults):
    pass


@dataclass
class TestCaseFailed(TestCaseResults):
    field: str
    error: str
