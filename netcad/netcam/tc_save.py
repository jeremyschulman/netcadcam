# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------
import json
from typing import List
from pathlib import Path
from dataclasses import asdict

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import aiofiles

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .tc_result_types import TestCasePass, TestCaseFailed, TestCaseInfo, TestCaseResults
from .dut import AsyncDeviceUnderTest

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["testcases_save_results"]

_map_result_type_str = {
    TestCasePass: "pass",
    TestCaseFailed: "fail",
    TestCaseInfo: "info",
}


async def testcases_save_results(
    dut: AsyncDeviceUnderTest,
    tc_name: str,
    results: List[TestCaseResults],
    resuls_dir: Path,
):
    results_file = resuls_dir / f"{tc_name}.json"
    json_payload = list()

    for res in results:
        res_dict = asdict(res)
        res_dict["type"] = _map_result_type_str[res.__class__]
        res_dict["device"] = dut.device.name
        res_dict["test_case"] = res_dict["test_case"].dict()
        json_payload.append(res_dict)

    async with aiofiles.open(results_file, "w+") as ofile:
        await ofile.write(json.dumps(json_payload, indent=3))
