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

__all__ = ["device_checks_save_results"]


async def device_checks_save_results(
    dut: AsyncDeviceUnderTest,
    filename: str,
    results: List[trt.CheckResult],
    results_dir: Path,
):
    """
    This function saves the testcase results to a JSON file.
    Parameters
    ----------
    dut:
        The device under test.

    filename:
        The name of the JSON file to save, without the .json extension.

    results:
        The list of testcase results.

    results_dir:
        The Path instance where the JSON file will be stored to the filesystem.

    """
    results_file = results_dir / f"{filename}.json"
    json_payload = list()

    for res in results:
        res_dict = res.dict()
        res_dict["device"] = dut.device.name
        res_dict["check"] = res_dict["check"]
        json_payload.append(res_dict)

    async with aiofiles.open(results_file, "w+") as ofile:
        await ofile.write(json.dumps(json_payload, indent=3))
