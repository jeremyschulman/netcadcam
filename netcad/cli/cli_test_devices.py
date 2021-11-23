# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------
import asyncio
from typing import Tuple
from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import Environment
from netcad.logger import get_logger
from netcad.cli.common_opts import opt_devices, opt_designs
from netcad.cli.device_inventory import get_devices_from_designs

from netcad.netcam.loader import import_netcam_plugin

from netcad.cli.netcam.cli_netcam_main import cli
from netcad.netcam import execute_testcases

# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@cli.command(name="test")
@opt_devices()
@opt_designs(required=True)
@click.option(
    "--tests-dir",
    help="location to read test-cases",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    envvar=Environment.NETCAD_TESTCASESDIR,
)
def cli_test_device(devices: Tuple[str], designs: Tuple[str], tests_dir: Path):
    """
    Execute tests to validate the operational state of devices.

    This command will use the device test cases to validate the running state
    compared to the expected states defined by the tests.

    \f
    Parameters
    ----------
    designs:
        The list of design names that should be processed by this command. All
        devices within the design will be processed, unless further filtered by
        the `devices` option.

    devices:
        The list of deice hostnames that should be processed by this command.

    tests_dir:
        The Path instance to the parent directory of test-cases.  Subdirectories
        exist for each device by hostname.
    """

    log = get_logger()

    netcam_plugin = import_netcam_plugin()
    get_dut = getattr(netcam_plugin, "get_dut")

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    duts = [get_dut(dev_obj) for dev_obj in device_objs]

    log.info(f"Starting tests for {len(device_objs)} devices.")

    async def go():
        await asyncio.gather(*(execute_testcases(dut) for dut in duts))

    asyncio.run(go())
