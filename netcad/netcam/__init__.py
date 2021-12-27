#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from .execute_checks import execute_device_checks

from netcad.checks.check_result_types import CheckFailResult, CheckResultsCollection


def any_failures(results):
    is_failure = lambda r: isinstance(r, CheckFailResult)
    return any(map(is_failure, results))
