from pydantic.dataclasses import dataclass
from .test_case import TestCase


@dataclass
class TestResults:
    test_case: TestCase


class TestPass(TestResults):
    test_results: dict


class TestFailed(TestResults):
    test_results: dict
