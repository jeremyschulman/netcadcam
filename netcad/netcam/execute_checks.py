# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from collections import Counter
from logging import Logger

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.cli.keywords import markup_color
from netcad.debug import debug_enabled, format_exc_message

from netcad.checks.check_result_types import CheckStatus, CheckSkipResult
from .save_check_results import device_checks_save_results
from .dut import AsyncDeviceUnderTest

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["execute_device_checks"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


PASS_CLRD = markup_color("PASS", "green")
FAIL_CLRD = markup_color("FAIL", "red")
SKIP_CLRD = markup_color("SKIP", "grey70")
SUMMARY_CLRD = markup_color("DONE", "bright_yellow")


async def execute_device_checks(dut: AsyncDeviceUnderTest):
    device = dut.device
    dev_name = device.name
    dut_name = f"{dev_name:<16}"

    log = get_logger()
    if not dut.testcases_dir.is_dir():
        log.error(
            f"{dut_name}:Missing expected checks directory: "
            f"{dut.testcases_dir.absolute()}, skipping"
        )
        return

    # -------------------------------------------------------------------------
    # Testing Prologue
    # -------------------------------------------------------------------------

    log.info(f"{dut_name}: Starting Checks ...")

    try:
        await dut.setup()

    except Exception as exc:
        errmsg = str(exc) or exc.__class__.__name__
        log.critical(
            f"{dut_name}: {FAIL_CLRD}:\t!!! Startup failed: {errmsg}, aborting."
        )

        if debug_enabled():
            log.critical(format_exc_message(exc))

        dut.result_counts["FAIL"] = 1
        log.info(f"{dut_name}: {SUMMARY_CLRD} ----\tChecks: PASS=0, FAIL=1, INFO=0")
        return

    # -------------------------------------------------------------------------
    # Execute all of the tests
    # -------------------------------------------------------------------------

    await run_tests(dut, log)

    # -------------------------------------------------------------------------
    # Testing Epilogue
    # -------------------------------------------------------------------------

    total_test_counts = dut.result_counts

    ttc = sum(total_test_counts.values())

    c_pass, c_fail, c_info, c_skip = (
        total_test_counts[CheckStatus.PASS],
        total_test_counts[CheckStatus.FAIL],
        total_test_counts[CheckStatus.INFO],
        total_test_counts[CheckStatus.SKIP],
    )

    log.info(
        f"{dut_name}: {SUMMARY_CLRD} {ttc:4}\tChecks: PASS={c_pass}, FAIL={c_fail}, INFO={c_info}, SKIP={c_skip}"
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


async def run_tests(dut: AsyncDeviceUnderTest, log: Logger):

    device = dut.device
    dev_tc_dir = dut.testcases_dir
    dut_name = f"{device.name:<16}"

    # -------------------------------------------------------------------------
    # Testing all Design Services and related Testing Services
    # -------------------------------------------------------------------------

    for ds_name, design_service in device.services.items():

        # there could be design services without defined testing services, so
        # skip if that is the case.

        if not design_service.check_collections:
            continue

        # log.info(f"{dut_name}: Design Service: {ds_name}")

        for testing_service in design_service.check_collections:

            tc_name = testing_service.get_name()
            tc_file = testing_service.filepath(testcase_dir=dev_tc_dir, service=tc_name)
            if not tc_file.exists():
                # if there are no test cases for this test-service, this
                # continue to the next one.  Deactivated the log message as not
                # sure if this is adding any value or potential confusion.  So
                # leaving it out for now.

                # log.info(f"{dut_name}: {SKIP_CLRD}\tTestcases: {tc_name}: None")
                continue

            testcases = await testing_service.load(testcase_dir=dev_tc_dir)

            if not len(testcases.checks):
                # if the test file was generated with an empty set of tests,
                # which could happen depending on the Developer of the testing
                # service, then skill this and go onto the next one.
                continue

            try:
                results = await dut.execute_testcases(testcases)

                # if the testing plugin returns None, then these tests are
                # marked as "skipped"

                if not results:
                    results = [
                        CheckSkipResult(
                            device=device,
                            message=f"Missing: device {device.name} support for "
                            f"Checks: {tc_name}",
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
            dut.result_counts.update(result_counts)

            c_pass, c_fail, c_info, c_skip = (
                result_counts[CheckStatus.PASS],
                result_counts[CheckStatus.FAIL],
                result_counts[CheckStatus.INFO],
                result_counts[CheckStatus.SKIP],
            )

            dev_resuls_dir = dev_tc_dir / "results"
            dev_resuls_dir.mkdir(exist_ok=True)

            if c_fail:
                log.warning(
                    f"{dut_name}: {FAIL_CLRD}\tChecks: {tc_name}: "
                    f"PASS={c_pass}, FAIL={c_fail}, INFO={c_info}",
                )
            elif c_skip:
                log.info(
                    f"{dut_name}: {SKIP_CLRD}\tChecks: {tc_name}",
                )
            else:
                log.info(
                    f"{dut_name}: {PASS_CLRD}\tChecks: {tc_name}: "
                    f"PASS={c_pass}, INFO={c_info}",
                )

            await device_checks_save_results(
                dut, tc_name, results, results_dir=dev_resuls_dir
            )
