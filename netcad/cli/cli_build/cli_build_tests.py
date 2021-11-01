# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple, List
import asyncio
from pathlib import Path
from logging import Logger

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.device import Device
from netcad.config import Environment

from netcad.cli.common_opts import opt_devices, opt_network
from netcad.cli import device_inventory

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


async def build_device_tests(device: Device, tc_dir: Path, log: Logger):
    log.info(f"Building tests for device: {device.name}")
    dev_tc_dir = tc_dir.joinpath(device.name)
    dev_tc_dir.mkdir(exist_ok=True)

    for service_obj in device.services:
        for tc_svccls in service_obj.testing_services:
            if not (test_cases := tc_svccls.build(device)):
                continue

            await test_cases.save(dev_tc_dir)


@clig_build.command(name="tests")
@opt_devices()
@opt_network()
@click.option(
    "--tests-dir",
    help="location to store configs",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    envvar=Environment.NETCAD_TESTCASESDIR,
)
def cli_build_tests(devices: Tuple[str], networks: Tuple[str], tests_dir: Path):
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
    networks
    tests_dir

    Returns
    -------
    """
    log = get_logger()

    # The set of devices we will build configurations for.  This set will be
    # sorted before the rendering process begins.

    device_objs = set()

    if devices:
        device_objs.update(device_inventory.get_devices(devices))

    if networks:
        device_objs.update(device_inventory.get_network_devices(networks))

    device_objs = [dev for dev in device_objs if not dev.is_pseudo]
    device_objs.sort()

    log.info(f"Building device audits for {len(device_objs)} devices")

    async def run():
        tasks = [
            asyncio.create_task(
                build_device_tests(
                    device=device,
                    tc_dir=tests_dir,
                    log=log,
                )
            )
            for device in device_objs
        ]
        await asyncio.gather(*tasks)

    asyncio.run(run())
