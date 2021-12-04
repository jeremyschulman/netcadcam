# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List
from collections import Counter

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.config import netcad_globals
from netcad.testing_services import TestCases

from .tc_result_types import TestCaseStatus, ResultsTestCase
from .tc_save import testcases_save_results
from .dut import AsyncDeviceUnderTest

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["execute_testcases"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

PASS_GREEN = "[green]PASS[/green]"
FAIL_RED = "[red]FAIL[/red]"
SKIP_BLUE = "[blue]SKIP[/blue]"


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

    for design_service in device.services.values():
        log.info(f"{dut_name}: Design Service: {design_service.__class__.__name__}")

        for testing_service in design_service.testing_services:
            tc_name = testing_service.get_service_name()

            testcases = await testing_service.load(testcase_dir=dev_tc_dir)

            # log.info(f"{dut_name}:\t\tTestcases: {tc_name}")

            try:
                results = await _gather_testcase_results(dut=dut, testcases=testcases)

            except Exception as exc:
                import traceback

                exc_info = traceback.format_tb(exc.__traceback__, -2)
                log.critical(
                    f"{dut_name}: Exception during exection: {exc}, aborting {tc_name}\n"
                    "\n".join(exc_info)
                )
                continue

            result_counts = Counter(r.status for r in results)

            c_pass, c_fail, c_info, c_skip = (
                result_counts[TestCaseStatus.PASS],
                result_counts[TestCaseStatus.FAIL],
                result_counts[TestCaseStatus.INFO],
                result_counts[TestCaseStatus.SKIP],
            )

            dev_resuls_dir = dev_tc_dir / "results"
            dev_resuls_dir.mkdir(exist_ok=True)

            if c_fail:
                log.warning(
                    f"{dut_name}: {FAIL_RED}\tTestcases: {tc_name}: "
                    f"PASS={c_pass}, FAIL={c_fail}, INFO={c_info}",
                    extra={"markup": True},
                )
            elif c_skip:
                log.info(
                    f"{dut_name}: {SKIP_BLUE}\tTestcases: {tc_name}",
                    extra={"markup": True},
                )
            else:
                log.info(
                    f"{dut_name}: {PASS_GREEN}\tTestcases: {tc_name}: "
                    f"PASS={c_pass}, INFO={c_info}",
                    extra={"markup": True},
                )

            await testcases_save_results(
                dut, tc_name, results, results_dir=dev_resuls_dir
            )

    # -------------------------------------------------------------------------
    # Testing Epilogue
    # -------------------------------------------------------------------------

    log.info(f"{dut_name}: Testing Completed.")

    try:
        await dut.teardown()

    except Exception as exc:
        log.error(f"{dut_name}: Teardown failed: {exc}")


# -----------------------------------------------------------------------------
#
#                          PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


async def _gather_testcase_results(
    dut: AsyncDeviceUnderTest, testcases: TestCases
) -> List[ResultsTestCase]:

    results = list()

    async for result in dut.execute_testcases(testcases):
        results.append(result)

    return results
