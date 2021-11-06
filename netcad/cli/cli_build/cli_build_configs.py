# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click
import jinja2

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
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
def cli_render(
    devices: Tuple[str], networks: Tuple[str], configs_dir: Path, output_console: bool
):
    """Build device configuration files"""

    log = get_logger()

    # The set of devices we will build configurations for.  This set will be
    # sorted before the rendering process begins.

    device_objs = set()

    if devices:
        device_objs.update(device_inventory.get_devices(devices))

    if networks:
        device_objs.update(device_inventory.get_network_devices(networks))

    # Filter out any device that is not a "real" device for configuration
    # purposes. for example the device representing an MLAG redundant pair. Then
    # sort the devices based on their sorting mechanism.

    if not (device_objs := sorted((dev for dev in device_objs if not dev.is_pseudo))):
        log.error("No devices for config building")
        return

    log.info(f"Building {len(device_objs)} device configurations.")
    log.info(f"Building device configs into directory: {configs_dir.absolute()}")

    for dev_obj in device_objs:

        config_file = configs_dir.joinpath(dev_obj.name + ".cfg")
        log.debug(f"BUILD config for device {dev_obj.name}")

        dev_obj.init_template_env()

        try:
            config_text = dev_obj.render_config()
            # template = dev_obj.get_template()
            # config_text = template.render(device=dev_obj)

        except jinja2.exceptions.TemplateNotFound as exc:
            raise RuntimeError(
                f"Jinja2 template not found error: {dev_obj.name} {dev_obj.template}  -  {str(exc)}"
            )

        except jinja2.exceptions.UndefinedError as exc:
            raise RuntimeError(
                f"Jinja2 undefined error: {dev_obj.name} {dev_obj.template}  -  {str(exc)}"
            )

        log.info(f"SAVE: {dev_obj.name} config: {config_file.name}")
        with config_file.open("w+") as ofile:
            ofile.write(config_text)

        if output_console:
            print(config_text, end="")
