#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.cli.common_opts import opt_devices, opt_designs
from netcad.cli.device_inventory import get_devices_from_designs
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


@clig_build.command(name="hostsfile")
@opt_designs()
@opt_devices()
def cli_build_hostsfile(
    devices: Tuple[str],
    designs: Tuple[str],
):
    """
    Create an /etc/hosts file content based on the design devices.
    """
    log = get_logger()

    if not (device_objs := get_devices_from_designs(designs, include_devices=devices)):
        log.error("No devices located in the given designs")
        return

    # Filter out any device that is not a "real" device for configuration
    # purposes. for example the device representing an MLAG redundant pair. Then
    # sort the devices based on their sorting mechanism.

    if not (
        device_objs := sorted(
            (dev for dev in device_objs if not any((dev.is_pseudo, dev.is_not_managed)))
        )
    ):
        log.error("No devices located in the given designs")
        return

    for dev_obj in device_objs:
        print(dev_obj.primary_ip, "\t", dev_obj.name)
