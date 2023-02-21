from typing import List, Dict
from netcad.checks import CheckStatus


def filter_results(results: dict, optionals: dict) -> List[Dict]:
    """
    This function filters the test cases results based on the User CLI flags.

    Parameters
    ----------
    results:
        The complete list of test case results.

    optionals:
        The User CLI option flags

    Returns
    -------
    List of the filtered results.  If the results include a "skip" indicator,
    then an empty list is returned.
    """
    inc_all = optionals["include_all"]

    if optionals["pass_only"]:
        status_allows = {CheckStatus.PASS}
    else:
        status_allows = {CheckStatus.FAIL}

    inc_fields = optionals["include_fields"]
    exc_fields = optionals["exclude_fields"]

    if optionals["include_info"] or inc_all:
        status_allows.add(CheckStatus.INFO)
        status_allows.add(CheckStatus.SKIP)

    if optionals["include_pass"] or inc_all:
        status_allows.add(CheckStatus.PASS)

    filter_flds_in = lambda i: i.get("field") in inc_fields
    filter_flds_out = lambda i: i.get("field") not in exc_fields
    filter_status = lambda i: i["status"] in status_allows

    results = filter(filter_status, results)

    if exc_fields:
        results = filter(filter_flds_out, results)

    if inc_fields:
        results = filter(filter_flds_in, results)

    return list(results)
