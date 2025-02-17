#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import json
from typing import List
from pathlib import Path
import asyncio

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import aiofiles

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.checks import CheckResult
from .dut import AsyncDeviceUnderTest
from netcam.db.db_check_results import db_check_results_save

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["device_checks_save_results"]


async def device_checks_save_results(
    dut: AsyncDeviceUnderTest,
    feat_name: str,
    filename: str,
    results: List[CheckResult],
    results_dir: Path,
):
    """
    This function saves the testcase results to a JSON file.
    Parameters
    ----------
    dut:
        The device under test.

    feat_name:
        The design feature name, "topology" for example.

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
        res.device = dut.device.name
        payload = res.model_dump(warnings="none")
        payload["check_id"] = res.check.check_id()
        json_payload.append(payload)

    # save the results to a local JSON file.

    async with aiofiles.open(results_file, "w+") as ofile:
        await ofile.write(json.dumps(json_payload, indent=3))

    await asyncio.to_thread(
        db_check_results_save,
        device=dut.device,
        feature_name=feat_name,
        collection=filename,
        results=json_payload,
    )
