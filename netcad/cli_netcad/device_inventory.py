# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Set, Sequence, List

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.cabling import CablePlanner
from netcad.init import loader

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
    designs: Sequence[str], include_devices: Sequence[str]
) -> List[Device]:

    for design_name in designs:
        loader.load_design(design_name=design_name)

    device_objs = sorted(Device.registry_items(True).values())

    if not include_devices:
        return device_objs

    return sorted([obj for obj in device_objs if obj.name in include_devices])


# TODO: remove
def get_devices(devices: Sequence[str]) -> Set[Device]:
    """
    Returns a set of Device objects corresponding to the list of
    hostnames provided.

    Parameters
    ----------
    devices: sequence[str]
        Set or list of strings

    Returns
    -------
    Set[Devices]

    Raises
    ------
    RuntimeError if any given device does not exist in the netcad inventory.
    """
    device_objs = set()

    for each_name in devices:
        if not (dev_obj := Device.registry_get(name=each_name)):
            raise RuntimeError(f"Device not found: {each_name}")

        device_objs.add(dev_obj)

    return device_objs


# TODO: remove
def get_network_devices(networks: Sequence[str]) -> Set[Device]:
    """
    Returns a set of Device objects that are members in any of the provided
    networks.

    Parameters
    ----------
    networks: sequence[str]
        Set or list of strings

    Returns
    -------
    Set[Devices]

    Raises
    ------
    RuntimeError if any given device does not exist in the netcad inventory.
    """

    device_objs = set()

    for each_network in networks:
        cabler: CablePlanner

        if not (cabler := CablePlanner.registry_get(name=each_network)):
            raise RuntimeError(f"Network not found: {each_network}")

        if not cabler.devices:
            raise RuntimeError(f"No devices found in network: {each_network}")

        device_objs.update(cabler.devices)

    return device_objs
