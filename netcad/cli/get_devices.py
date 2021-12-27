#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Sequence, List

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["get_devices"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def get_devices(device_list: Sequence[str]) -> List[Device]:
    dev_objs: List[Device] = list()

    for dev_name in device_list:
        if not (dev_obj := Device.registry_get(dev_name)):
            raise RuntimeError(f"Device not found in registry: {dev_name}")

        dev_objs.append(dev_obj)

    return dev_objs
