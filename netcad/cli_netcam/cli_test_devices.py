# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

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
from netcad.init.loader import load_design
from netcad.cli_netcad.common_opts import opt_devices, opt_designs
from netcad.cli_netcad.device_inventory import get_network_devices

from netcad.cli_netcam.main import cli

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

    for design_name in designs:
        load_design(design_name=design_name)

    device_objs = get_network_devices(designs)
    if devices:
        device_objs = [obj for obj in device_objs if obj.name in devices]

    print(f"Starting tests for {len(device_objs)} devices.")
