from .tc_execute import execute_design_checks

from .tc_result_types import (
    CheckResultsCollection,
    CheckPassResult,
    CheckFailResult,
    CheckFailNoExists,
    CheckFailFieldMismatch,
    CheckFailMissingMembers,
    CheckFailExtraMembers,
    CheckInfoLog,
    CheckResult,
    CheckSkipResult,
)


def any_failures(results):
    is_failure = lambda r: isinstance(r, CheckFailResult)
    return any(map(is_failure, results))
