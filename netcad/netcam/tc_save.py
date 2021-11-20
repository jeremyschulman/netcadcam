# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import json
from typing import List
from pathlib import Path


# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import aiofiles

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from . import tc_result_types as trt
from .dut import AsyncDeviceUnderTest

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["testcases_save_results"]


async def testcases_save_results(
    dut: AsyncDeviceUnderTest,
    tc_name: str,
    results: List[trt.TestCaseResults],
    resuls_dir: Path,
):
    results_file = resuls_dir / f"{tc_name}.json"
    json_payload = list()

    for res in results:
        res_dict = res.dict()
        res_dict["type"] = _map_result_type_str(res)
        res_dict["device"] = dut.device.name
        res_dict["test_case"] = res_dict["test_case"]
        json_payload.append(res_dict)

    async with aiofiles.open(results_file, "w+") as ofile:
        await ofile.write(json.dumps(json_payload, indent=3))


def _map_result_type_str(tr_type: trt.TestCaseResults):

    if isinstance(tr_type, trt.TestCasePass):
        return "PASS"

    if isinstance(tr_type, trt.TestCaseFailed):
        return "FAIL"

    if isinstance(tr_type, trt.TestCaseInfo):
        return "INFO"

    return "UNKNOWN"
