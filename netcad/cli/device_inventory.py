# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Sequence, List, Optional

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.design_services import load_design

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

    device_objs = set()
    for design_name in designs:
        design_ctx = load_design(design_name=design_name)
        design_obj = design_ctx["obj"]
        device_objs.update(design_obj.devices.values())

    # device_objs = sorted(
    #     obj for obj in Device.registry_items(True).values() if isinstance(obj, Device)
    # )

    if not include_devices:
        return sorted(device_objs)

    return sorted([obj for obj in device_objs if obj.name in include_devices])
