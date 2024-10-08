#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Sequence
from copy import deepcopy
from dataclasses import dataclass
from ipaddress import IPv4Interface
from pathlib import Path

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device.profiles import InterfaceL3
from netcad.device.device_group import DeviceGroup, DeviceGroupMember

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "DeviceMLagPairGroup", "DeviceMLagGroupMember", "DeviceMLagPairGroupConfig",
    "DeviceMLagPairGroupLocalInterfaceConfig"
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class DeviceMLagGroupMember(DeviceGroupMember):
    device_id: int
    is_mlag_device = True

#
# @dataclass
# class DeviceMLagPairGroupLocalInterfaceConfig:
#     name: str
#     vlan_id: int
#     subnet: IPv4Interface
#     template: Path

@dataclass
class DeviceMLagPairGroupConfig:

    @dataclass
    class LocalInterface:
        name: str
        vlan_id: int
        subnet: IPv4Interface
        template: Path

    domain_id: str
    local_interface: LocalInterface
    peer_link: str


class DeviceMLagPairGroup(DeviceGroup):
    is_mlag_group = True

    def __init__(
        self,
        name: str,
        config: DeviceMLagPairGroupConfig,
        devices: Optional[Sequence["DeviceMLagGroupMember"]] = None,
        **kwargs,
    ):
        super(DeviceMLagPairGroup, self).__init__(name, **kwargs)
        self.config = config
        for device_id, dev in enumerate(devices, start=1):
            dev.device_id = device_id
            self.add_group_member(dev)

        self.set_local_interface()

    def set_local_interface(self):
        if_name = self.config.local_interface.name

        for dev in self.group_members:
            with dev.interfaces[if_name] as if_lcl:
                if_subnet = self.config.local_interface.subnet
                if_ipaddr = IPv4Interface((if_subnet.ip + dev.device_id, if_subnet.network.prefixlen))
                if_lcl.profile = InterfaceL3(
                    desc="MLAG peering interface",
                    if_ipaddr=if_ipaddr,
                    template=self.config.local_interface.template,
            )

        dev1, dev2 = self.group_members
        dev1.interfaces[if_name].cable_peer = dev2.interfaces[if_name]
        dev2.interfaces[if_name].cable_peer = dev1.interfaces[if_name]

    def build(self):
        """
        The build process is used to "copy" any interface profiles defined in
        the MLag Device Group into each of the Device Members (2).  This
        process needs to be called before the calbing process is called so that
        the cabling process can create the cable_peer assignments.
        """

        if not (count := len(self.group_members)) == 2:
            raise RuntimeError(
                f"Unexpected number of devices in device group: {self.name}: {count}"
            )

        # create the association between each of the interfaces defined in the
        # rendudant pair and the associated concrete device. This copies only
        # the interface profile, and no other interface attributes.  The cable
        # associations will be made by the cable planner.

        for if_name, dg_iface_obj in self.interfaces.items():
            for device in self.group_members:
                if not (dg_if_prof := getattr(dg_iface_obj, "profile", None)):
                    continue

                copy_if_pro = deepcopy(dg_if_prof)

                # remove the interface back-ref so that the interface profile
                # can be assigned to the physical device interface; otherwise
                # there is a RuntimeError that checks duplicate assignment.

                copy_if_pro.interface = None

                # now assign the interface profile to the concrete device
                # interface object.

                device.interfaces[if_name].profile = copy_if_pro
