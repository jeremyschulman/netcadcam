from .execute_checks import execute_device_checks

from netcad.checks.check_result_types import CheckFailResult, CheckResultsCollection


def any_failures(results):
    is_failure = lambda r: isinstance(r, CheckFailResult)
    return any(map(is_failure, results))
