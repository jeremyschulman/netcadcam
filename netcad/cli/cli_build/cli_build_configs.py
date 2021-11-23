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
from netcad.cli.common_opts import opt_devices, opt_designs

from ..device_inventory import get_devices_from_designs
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
@opt_designs(required=True)
@opt_devices()
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
    devices: Tuple[str], designs: Tuple[str], configs_dir: Path, output_console: bool
):
    """Build device configuration files"""

    log = get_logger()

    # Load the specified designs.  As a result the Device registry will be populated
    # accordingly.  Extract the device objects from the registry into a set that
    # we can then iterate through.

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    # Filter out any device that is not a "real" device for configuration
    # purposes. for example the device representing an MLAG redundant pair. Then
    # sort the devices based on their sorting mechanism.

    if not (device_objs := sorted((dev for dev in device_objs if not dev.is_pseudo))):
        log.error("No devices located in the given designs")
        return

    log.info(f"Building {len(device_objs)} device configurations.")
    log.info(f"Building device configs into directory: {configs_dir.absolute()}")

    for dev_obj in device_objs:

        config_file = configs_dir.joinpath(dev_obj.name + ".cfg")
        if not dev_obj.template:
            log.warning(
                f"BUILD SKIP: device {dev_obj.name} - no template file defined."
            )
            continue

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
