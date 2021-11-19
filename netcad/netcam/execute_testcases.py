from netcad.logger import get_logger
from netcad.config import netcad_globals


from .dut import AsyncDeviceUnderTest


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

    log.info(f"{dut_name}: Starting Tests ...")

    for design_service in device.services:
        log.info(f"{dut_name}:    Design Service: {design_service.__class__.__name__}")
        for testing_service in design_service.testing_services:
            log.info(
                f"{dut_name}:        Testcases: {testing_service.get_service_name()}"
            )

    log.info(f"{dut_name}: Testing Completed.")
