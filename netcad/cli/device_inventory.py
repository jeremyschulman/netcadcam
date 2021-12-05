# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Sequence, List, Optional

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.init import load_design

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["get_devices_from_designs"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def get_devices_from_designs(
    designs: Sequence[str], include_devices: Optional[Sequence[str]] = None
) -> List[Device]:

    for design_name in designs:
        load_design(design_name=design_name)

    device_objs = sorted(
        obj for obj in Device.registry_items(True).values() if isinstance(obj, Device)
    )

    if not include_devices:
        return device_objs

    return sorted([obj for obj in device_objs if obj.name in include_devices])
