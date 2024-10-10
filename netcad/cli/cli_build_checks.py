#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple, List
import asyncio
from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.config import Environment
from netcad.cli.common_opts import opt_devices, opt_designs
from netcad.device import Device
from netcad.design import load_design

from .clig_build import clig_build

# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

DevicesList = List[Device]


@clig_build.command(name="checks")
@opt_devices()
@opt_designs()
@click.option(
    "--save-dir",
    "checks_dir",
    help="location to store generated checks",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    envvar=Environment.NETCAD_CHECKSDIR,
)
def cli_build_tests(devices: Tuple[str], designs: Tuple[str], checks_dir: Path):
    """
    Build device test cases to audit live network

    This command generates the device audit test cases.  These are collections
    of JSON files that indicate each of the specific tests that will be run
    against the live network.  The command to execute these tests is `netcad
    audit device` or `netcad audit network`.
    """
    log = get_logger()

    # The set of devices we will build configurations for.  This set will be
    # sorted before the rendering process begins.

    # Load the specified designs.  As a result the Device registry will be populated
    # accordingly.  Extract the device objects from the registry into a set that
    # we can then iterate through.

    for design_name in designs:
        design = load_design(design_name=design_name)

    device_objs = design.devices.values()  # noqa

    if devices:
        device_objs = [obj for obj in device_objs if obj.name in devices]

    device_objs = [
        dev for dev in device_objs if not any((dev.is_pseudo, dev.is_not_managed))
    ]
    device_objs.sort()

    log.info(f"Building device audits for {len(device_objs)} devices")

    async def run():
        tasks = [
            asyncio.create_task(
                _build_device_checks(
                    device=device,
                    tc_dir=checks_dir,
                )
            )
            for device in device_objs
        ]
        await asyncio.gather(*tasks)

    asyncio.run(run())


# -----------------------------------------------------------------------------
#
#                                 PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


async def _build_device_checks(device: Device, tc_dir: Path):
    """
    This function is used to build the collection of test-case files for the
    given device.  The collection of test-cases will be stored as JSON files,
    the directory will be the name as the device.name.

    Parameters
    ----------
    device:
        The specific device instance.  Note that the device.name must not
        contain any special characters that would complicate the directory
        creation process.

    tc_dir: Path
        The path instance to the top-level test-case directory where the
        device-specific directory will be created.
    """
    log = get_logger()

    log.info(f"Building checks for device: {device.name}")

    # the checks directory for the device is a subdir under the design-name.
    # ensure this directory path exists.

    dev_tc_dir = tc_dir / device.design.name / device.name
    dev_tc_dir.mkdir(parents=True, exist_ok=True)

    # for each service that is bound on the device, iterate over each of the
    # testing features associated with that service; build the test-cases for
    # the device and save to a JSON data file.
    for service_obj in device.features.values():
        for tc_svccls in service_obj.check_collections:
            if not (test_cases := tc_svccls.build(device, design_feature=service_obj)):
                continue
            await test_cases.save(dev_tc_dir)
