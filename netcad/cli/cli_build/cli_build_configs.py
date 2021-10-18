# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------
import os
from typing import Tuple
import sys
from pathlib import Path
from setuptools import find_packages
from importlib import import_module

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.cabling import CablePlanner
from netcad.device import Device
from netcad.jinja2.env import get_env
from netcad.logger import get_logger
from netcad.config import Environment
from netcad.cli.main import clig_build

from netcad.cli.common_opts import opt_devices, opt_network

# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_build.command(name="configs")
@opt_devices()
@opt_network()
@click.option(
    "--configs-dir",
    help="location to store configs",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    default="configs",
)
@click.option(
    "--console", "output_console", help="display output to console", is_flag=True
)
def cli_render(devices: Tuple[str], networks: Tuple[str], configs_dir: Path, output_console: bool):
    """Build device configuration files"""

    log = get_logger()

    # The set of devices we will build configurations for.  This set will be
    # sorted before the rendering process begins.

    device_objs = set()

    if devices:
        for each_name in devices:
            if not (dev_obj := Device.registry_get(name=each_name)):
                log.error(f"Device not found: {each_name}")
                return

            device_objs.add(dev_obj)

    if networks:
        for each_network in networks:
            cabler: CablePlanner

            if not (cabler := CablePlanner.registry_get(name=each_network)):
                log.error(f"Network not found: {each_network}")
                return

            if not cabler.devices:
                log.error(f"No devices found in network: {each_network}")
                return

            device_objs.update(cabler.devices)

    # Filter out any device that is not a "real" device for configuration
    # purposes. for example the device representing an MLAG redundant pair. Then
    # sort the devices based on their sorting mechanism.

    device_objs = sorted(filter(lambda d: not hasattr(d, 'no_config'), device_objs))

    # Find all of the template directories walking down the $NETCAD_PROJECTDIR.
    # Reverse this list so that the "nearest" template directory is used first;
    # presuming there could be a filename clash.  TODO: rethink this approach.

    template_dirs = list(Path(os.environ[Environment.NETCAD_PROJECTDIR]).rglob('**/templates'))
    template_dirs.reverse()
    template_dirs.append('/')
    env = get_env(template_dirs)

    log.info(f"Building device configs into directory: {configs_dir.absolute()}")
    for dev_obj in device_objs:
        config_file = configs_dir.joinpath(dev_obj.name + ".cfg")
        log.debug(f"BUILD config for device {dev_obj.name}")

        template = dev_obj.get_template(env=env)
        config_text = template.render(device=dev_obj)

        log.info(f"SAVE: {dev_obj.name} config: {config_file.name}")
        with config_file.open("w+") as ofile:
            ofile.write(config_text)

        if output_console:
            print(config_text, end="")
