from .tc_execute import execute_testcases

from .tc_result_types import (
    CollectionTestResults,
    PassTestCase,
    FailTestCase,
    FailNoExistsResult,
    FailFieldMismatchResult,
    FailMissingMembersResult,
    FailExtraMembersResult,
    InfoTestCase,
    ResultsTestCase,
    SkipTestCases,
)


def any_failures(results):
    is_failure = lambda r: isinstance(r, FailTestCase)
    return any(map(is_failure, results))
