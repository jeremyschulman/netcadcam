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

from netcad.init import loader
from netcad.logger import get_logger
from netcad.config import Environment
from netcad.cli.common_opts import opt_devices, opt_designs
from netcad.device import Device

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


async def build_device_tests(device: Device, tc_dir: Path):
    """
    This function is used to build the collection of test-case files for the
    given device.  The collection of test-cases will be stored as JSON files,
    the directory will be the name name as the device.name.

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

    log.info(f"Building tests for device: {device.name}")

    # create a per-device directory to store the collection of test-case files.

    dev_tc_dir = tc_dir.joinpath(device.name)
    dev_tc_dir.mkdir(exist_ok=True)

    # for each service that is bound on the device, iterate over each of the
    # testing services associated with that service; build the test-cases for
    # the device and save to a JSON data file.

    for service_obj in device.services.values():
        for tc_svccls in service_obj.testing_services:
            if not (test_cases := tc_svccls.build(device, service=service_obj)):
                continue

            await test_cases.save(dev_tc_dir)


@clig_build.command(name="tests")
@opt_devices()
@opt_designs()
@click.option(
    "--tests-dir",
    help="location to store test-cases",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    envvar=Environment.NETCAD_TESTCASESDIR,
)
def cli_build_tests(devices: Tuple[str], designs: Tuple[str], tests_dir: Path):
    """
    Build device test cases to audit live network

    This command generates the device audit test cases.  These are collections
    of JSON files that indicate each of the specific tests that will be run
    against the live network.  The command to execute these tests is `netcad
    audit device` or `netcad audit network`.
    \f

    Parameters
    ----------
    devices
    designs
    tests_dir
    """
    log = get_logger()

    # The set of devices we will build configurations for.  This set will be
    # sorted before the rendering process begins.

    # Load the specified designs.  As a result the Device registry will be populated
    # accordingly.  Extract the device objects from the registry into a set that
    # we can then iterate through.

    for design_name in designs:
        loader.load_design(design_name=design_name)

    device_objs = set(Device.registry_items(True).values())
    if devices:
        device_objs = [obj for obj in device_objs if obj.name in devices]

    device_objs = [dev for dev in device_objs if not dev.is_pseudo]
    device_objs.sort()

    log.info(f"Building device audits for {len(device_objs)} devices")

    async def run():
        tasks = [
            asyncio.create_task(
                build_device_tests(
                    device=device,
                    tc_dir=tests_dir,
                )
            )
            for device in device_objs
        ]
        await asyncio.gather(*tasks)

    asyncio.run(run())
