# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from collections import Counter

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.config import netcad_globals
from netcad.cli.keywords import markup_color

from .tc_result_types import TestCaseStatus, SkipTestCases
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


PASS_CLRD = markup_color("PASS", "green")
FAIL_CLRD = markup_color("FAIL", "red")
SKIP_CLRD = markup_color("SKIP", "grey70")
SUMMARY_CLRD = markup_color("DONE", "bright_yellow")


async def execute_testcases(dut: AsyncDeviceUnderTest):
    device = dut.device
    dev_name = device.name
    dut_name = f"DUT: {dev_name}"

    total_test_counts = dut.result_counts

    # TODO: remove this; the tc_dir is setup during the call to
    #       execute_testcases.
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

    for ds_name, design_service in device.services.items():

        # there could be design services without defined testing services, so
        # skip if that is the case.

        if not design_service.testing_services:
            continue

        # log.info(f"{dut_name}: Design Service: {ds_name}")

        for testing_service in design_service.testing_services:

            tc_name = testing_service.get_service_name()
            tc_file = testing_service.filepath(testcase_dir=dev_tc_dir, service=tc_name)

            if not tc_file.exists():
                log.info(f"{dut_name}: {SKIP_CLRD}\tTestcases: {tc_name}: None")
                continue

            testcases = await testing_service.load(testcase_dir=dev_tc_dir)

            try:
                results = await dut.execute_testcases(testcases)

                # if the testing plugin returns None, then these tests are
                # marked as "skipped"

                if not results:
                    results = [
                        SkipTestCases(
                            device=device,
                            message=f"Missing: device {device.name} support for "
                            f"testcases: {tc_name}",
                        )
                    ]

            except Exception as exc:
                import traceback

                exc_info = traceback.format_tb(exc.__traceback__, -2)
                log.critical(
                    f"{dut_name}: Exception during exection: {exc}, aborting {tc_name}\n"
                    "\n".join(exc_info)
                )
                continue

            result_counts = Counter(r.status for r in results)
            total_test_counts.update(result_counts)

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
                    f"{dut_name}: {FAIL_CLRD}\tTestcases: {tc_name}: "
                    f"PASS={c_pass}, FAIL={c_fail}, INFO={c_info}",
                )
            elif c_skip:
                log.info(
                    f"{dut_name}: {SKIP_CLRD}\tTestcases: {tc_name}",
                )
            else:
                log.info(
                    f"{dut_name}: {PASS_CLRD}\tTestcases: {tc_name}: "
                    f"PASS={c_pass}, INFO={c_info}",
                )

            await testcases_save_results(
                dut, tc_name, results, results_dir=dev_resuls_dir
            )

    # -------------------------------------------------------------------------
    # Testing Epilogue
    # -------------------------------------------------------------------------

    ttc = sum(total_test_counts.values())

    c_pass, c_fail, c_info, c_skip = (
        total_test_counts[TestCaseStatus.PASS],
        total_test_counts[TestCaseStatus.FAIL],
        total_test_counts[TestCaseStatus.INFO],
        total_test_counts[TestCaseStatus.SKIP],
    )

    log.info(
        f"{dut_name}: {SUMMARY_CLRD} {ttc:4}\tTestcases: PASS={c_pass}, FAIL={c_fail}, INFO={c_info}"
    )

    try:
        await dut.teardown()

    except Exception as exc:
        log.error(f"{dut_name}: Teardown failed: {exc}")


# -----------------------------------------------------------------------------
#
#                          PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------

# TODO: remove
# async def _gather_testcase_results(
#     dut: AsyncDeviceUnderTest, testcases: TestCases
# ) -> List[ResultsTestCase]:
#
#     results = list()
#
#     async for result in dut.execute_testcases(testcases):
#         results.append(result)
#
#     return results
