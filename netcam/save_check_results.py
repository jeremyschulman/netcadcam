#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

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

from netcad.checks import CheckResult
from .dut import AsyncDeviceUnderTest

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["device_checks_save_results"]


async def device_checks_save_results(
    dut: AsyncDeviceUnderTest,
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

    filename:
        The name of the JSON file to save, without the .json extension.

    results:
        The list of testcase results.

    results_dir:
        The Path instance where the JSON file will be stored to the filesystem.

    """
    results_file = results_dir / f"{filename}.json"
    json_payload = list()

    # we need to double-pump the pydantic data check results so that we can
    # take advantage of the pydantic custom JSON serializers and encoder
    # features; for example for the check-result logs.
    # TODO: research if there is a way to avoid the double-pump;
    #       probably need to create a pydantic object to represent a list of
    #       check results ;-)

    for res in results:
        res.device = dut.device.name
        json_payload.append(json.loads(json.dumps(res.model_dump(warnings="none"))))

    async with aiofiles.open(results_file, "w+") as ofile:
        await ofile.write(json.dumps(json_payload, indent=3))
