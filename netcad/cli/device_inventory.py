# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Set, Sequence

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.cabling import CablePlanner

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["get_devices", "get_network_devices"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def get_devices(devices: Sequence[str]) -> Set[Device]:
    device_objs = set()

    for each_name in devices:
        if not (dev_obj := Device.registry_get(name=each_name)):
            raise RuntimeError(f"Device not found: {each_name}")

        device_objs.add(dev_obj)

    return device_objs


def get_network_devices(networks: Sequence[str]) -> Set[Device]:
    device_objs = set()

    for each_network in networks:
        cabler: CablePlanner

        if not (cabler := CablePlanner.registry_get(name=each_network)):
            raise RuntimeError(f"Network not found: {each_network}")

        if not cabler.devices:
            raise RuntimeError(f"No devices found in network: {each_network}")

        device_objs.update(cabler.devices)

    return device_objs
