# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import typing as t

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, DeviceInterface
from netcad.vlan_profile import SENTIAL_ALL_VLANS, VlanProfile


def j2_filter_vlans_used(
    obj: t.Union[Device, DeviceInterface], scope="vlans"
) -> t.Union[t.List[VlanProfile], VlanProfile]:

    # get the attribute value for the named "scope"

    if not (attr_val := getattr(obj.profile, scope, None)):
        raise RuntimeError(f"Missing interface profile attribute: {obj.name}: {scope}")

    if isinstance(obj, Device):
        # return all VLANs used by this devicea
        # TODO: we could be more specific with different scopes; but for now
        #       there are not any at the device level.
        return obj.vlans()

    if isinstance(obj, DeviceInterface):
        if not isinstance(attr_val, t.Sequence):
            return attr_val

    return obj.device.vlans() if SENTIAL_ALL_VLANS in attr_val else attr_val
