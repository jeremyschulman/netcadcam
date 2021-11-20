# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------
import json
from typing import List, Tuple
from collections import defaultdict
from pathlib import Path
from dataclasses import asdict

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import aiofiles

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.config import netcad_globals
from netcad.testing_services import TestCases
from .tc_results import TestCasePass, TestCaseFailed, TestCaseInfo, TestCaseResults

from .dut import AsyncDeviceUnderTest


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

PASS_GREEN = "[green]PASS[/green]"
FAIL_RED = "[red]FAIL[/red]"


async def gather_testcase_results(
    dut: AsyncDeviceUnderTest, testcases: TestCases
) -> Tuple[List[TestCaseResults], defaultdict]:

    results = list()
    result_counts = defaultdict(int)

    async for result in dut.execute_testcases(testcases):
        results.append(result)
        result_counts[result.__class__] += 1

    return results, result_counts


_map_result_type_str = {
    TestCasePass: "pass",
    TestCaseFailed: "fail",
    TestCaseInfo: "info",
}


async def save_testcase_results(
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


async def execute_testcases(dut: AsyncDeviceUnderTest):
    device = dut.device
    dev_name = device.name
    dut_name = f"DUT:{dev_name}"

    tc_dir = netcad_globals.g_netcad_testcases_dir

    log = get_logger()

    dev_tc_dir = tc_dir / dev_name
    if not dev_tc_dir.is_dir():
        log.error(
            f"{dut_name}:Missing expected testcase directory: {dev_tc_dir.absolute()}, skipping"
        )
        return

    # -------------------------------------------------------------------------
    # Testing Prologue
    # -------------------------------------------------------------------------

    log.info(f"{dut_name}: Starting Tests ...")

    try:
        await dut.setup()

    except Exception as exc:
        log.error(f"{dut_name}: Startup failed: {exc}, aborting.")
        return

    # -------------------------------------------------------------------------
    # Testing all Design Services and related Testing Services
    # -------------------------------------------------------------------------

    for design_service in device.services:
        log.info(f"{dut_name}:    Design Service: {design_service.__class__.__name__}")

        for testing_service in design_service.testing_services:
            tc_name = testing_service.get_service_name()

            # TODO: move this 'limiter' once all of the testing code is
            #       implmeneted.
            #       v----------------------------------------------------------
            if tc_name not in ("device",):
                log.warning(f"{dut_name}:        Testcases: {tc_name}, skipping")
                continue
            # TODO: remove ^---------------------------------------------------

            log.info(f"{dut_name}:        Testcases: {tc_name}")

            testcases = await testing_service.load(testcase_dir=dev_tc_dir)

            try:
                results, result_counts = await gather_testcase_results(
                    dut=dut, testcases=testcases
                )
            except Exception as exc:
                log.error(
                    f"{dut_name}: Exception during exection: {exc}, aborting {tc_name}"
                )
                continue

            dev_resuls_dir = dev_tc_dir / "results"
            dev_resuls_dir.mkdir(exist_ok=True)

            if result_counts[TestCaseFailed] == 0:
                log.info(
                    f"{dut_name}:        {PASS_GREEN}/Testcases: {tc_name}: "
                    f"pass={result_counts[TestCasePass]}, "
                    f"info={result_counts[TestCaseInfo]}",
                    extra={"markup": True},
                )
            else:
                log.warning(
                    f"{dut_name}:        {FAIL_RED}/Testcases: {tc_name}: "
                    f"pass={result_counts[TestCasePass]}, "
                    f"info={result_counts[TestCaseInfo]}, "
                    f"failed={result_counts[TestCaseFailed]}",
                    extra={"markup": True},
                )

            await save_testcase_results(
                dut, tc_name, results, resuls_dir=dev_resuls_dir
            )

    # -------------------------------------------------------------------------
    # Testing Epilogue
    # -------------------------------------------------------------------------

    log.info(f"{dut_name}: Testing Completed.")

    try:
        await dut.teardown()

    except Exception as exc:
        log.error(f"{dut_name}: Teardown failed: {exc}")
