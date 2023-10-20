from typing import Optional
from netcad.device import Device


def cable_id_maker(
    device_1: Device, device_2: Device, link_id: int = 1, id_type: Optional[str] = None
) -> str:
    """
    This function creates a string cable_id value based on the device hostnames
    and the link_id.  The devices are always sorted so that regardless of the
    order of the devices in the parameters the same cable_id value is created
    for the same devices, link-id.

    The format of the cable id is "<device1.name>_<device2.name>_<link_id>"
    when id_type is None.  Otherwise, the format is
    "<device1.name>_<device2.name>_<id_type>_<link_id>"

    Parameters
    ----------
    device_1:
        The first device

    device_2:
        The second device

    link_id:
        The numeric identifier for the link count.  If there is only one link
        between the two devices, then the value is 1.  If there are two links
        between the devices, then link_id would be 1 for the first and 2 for
        second.  And so on.

    id_type:
        This value is used to designate the type of the cable/link.  For standard
        phyiscal links this value should be left as the default empty-string.  For
        other types, such as port-channels, the Caller can use a value to designate
        these differently.  For port-channels, they might choose to set id_type='po'
    Returns
    -------

    """
    _dev1, _dev2 = sorted((device_1, device_2))
    return (
        f"{_dev1.name}_{_dev2.name}_{link_id}"
        if not id_type
        else f"{_dev1.name}_{_dev2.name}_{id_type}_{link_id}"
    )
