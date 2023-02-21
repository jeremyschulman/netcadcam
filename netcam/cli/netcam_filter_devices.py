#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Sequence, List

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.logger import get_logger

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["netcam_filter_devices"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def netcam_filter_devices(device_objs: Sequence[Device]) -> List[Device]:
    """
    This function is used to return only those devices in the design that the
    system _should_ be able to communicate with.  From the list of provided
    devices, this function will remove any device missing its primary IP, or
    any device that is designated as pseudo-device (that is, not an actual
    device to communicate with).
    """

    # remove any "non" device, such as device-groups that represent MLAGs.
    device_objs = {dev for dev in device_objs if not dev.is_pseudo}

    # remove any devices that do not have their primary IP assigned so that we
    # do not try to use it.

    if devs_no_primary_ip := {dev for dev in device_objs if not dev.primary_ip}:
        no_primary_ip_names = ", ".join(dev.name for dev in devs_no_primary_ip)
        get_logger().warning(
            f"SKIP, devices that are missing primary-IP assignment: {no_primary_ip_names}"
        )
        device_objs -= devs_no_primary_ip

    # return the sorted list of device object
    return sorted(device_objs)
