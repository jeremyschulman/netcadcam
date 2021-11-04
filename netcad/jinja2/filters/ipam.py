from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netcad.device import DeviceInterface


def ipam_interface(interface: "DeviceInterface"):
    ipaddress = getattr(interface, "ipaddress", None)

    if not ipaddress:
        raise RuntimeError(
            f"ipam_interface: {interface.device.name} {interface.name}: no ipaddress assigned."
        )

    return str(ipaddress)
