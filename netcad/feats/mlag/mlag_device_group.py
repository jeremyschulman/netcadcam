#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Sequence, Type
from copy import deepcopy
from dataclasses import dataclass
from ipaddress import IPv4Interface
from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from first import first

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import DeviceInterface
from netcad.device.profiles import InterfaceProfile
from netcad.device.device_group import DeviceGroup, DeviceGroupMember
from netcad.feats.vlans import InterfaceVlan, VlanProfile

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "DeviceMLagPairGroup",
    "DeviceMLagGroupMember",
    "DeviceMLagPairGroupConfig",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class DeviceMLagGroupMember(DeviceGroupMember):
    device_id: int
    is_mlag_device = True



@dataclass
class DeviceMLagPairGroupConfig:
    @dataclass
    class LocalInterface:
        name: str
        vlan: VlanProfile
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
                if_ipaddr = IPv4Interface(
                    (if_subnet.ip + dev.device_id, if_subnet.network.prefixlen)
                )
                if_lcl.profile = InterfaceVlan(
                    desc="MLAG peering interface",
                    vlan=self.config.local_interface.vlan,
                    if_ipaddr=if_ipaddr,
                    template=self.config.local_interface.template,
                )

        dev1, dev2 = self.group_members
        dev1.interfaces[if_name].cable_peer = dev2.interfaces[if_name]
        dev2.interfaces[if_name].cable_peer = dev1.interfaces[if_name]

    def build_mlag(
        self,
        if_alias: str,
        if_profile: Type[InterfaceProfile],
        peer_intf: DeviceInterface,
    ):
        """
        This function is used to build an MLAG connection between the Mlag
        redundant device and a peer Device interface.

        Parameters
        ----------
        if_alias:
            The name of the MLAG device interface alias.

        if_profile:
            The profile to create on the MLAG device interface.

        peer_intf:
            The peer interface to cable to the MLAG device interface.
        """

        # for each Device in the MLAG device group, create a cable relationship
        # between the device interface and the peer interface.

        for my_dev in self.group_members:
            my_dev_intf = my_dev.interfaces.alias(if_alias)
            my_dev_intf.cable_peer = peer_intf
            peer_intf.cable_peer = self.interfaces[my_dev_intf.name]

        # create a cable relationship between the MLAG device interface and the
        # peer interface.

        mlag_ifname = my_dev_intf.name  # noqa
        self.interfaces[mlag_ifname].profile = if_profile()
        self.interfaces[mlag_ifname].cable_peer = peer_intf

    def build_mlag2mlag(
        self,
        if_alias: str,
        if_profile: Type[InterfaceProfile],
        peer_mlag_dev: "DeviceMLagPairGroup",
        peer_if_alias: str,
        peer_if_profile: Type[InterfaceProfile],
    ):
        # get the interface name for the MLAG device that will be used to build
        # the cabling relationship.  Use the first device in the device group
        # to reference the interface alias mapping since the device-group does
        # not have one.

        my_dev0 = first(self.group_members)
        mlag_if_name = my_dev0.interfaces_map[if_alias]

        # get the remote device interface name from the alias.

        rmt01, rmt02 = peer_mlag_dev.group_members
        peer_if_ame = rmt01.interfaces_map[peer_if_alias]

        # create profiles on each of the MLAG device-group pseudo-mlag
        # interfaces.

        self.interfaces[mlag_if_name].profile = if_profile()
        peer_mlag_dev.interfaces[peer_if_ame].profile = peer_if_profile()

        # cable the pseudo port-channels to each other.

        self.interfaces[mlag_if_name].cable_peer = peer_mlag_dev.interfaces[peer_if_ame]
        peer_mlag_dev.interfaces[peer_if_ame].cable_peer = self.interfaces[mlag_if_name]

        # for each of the Devices in the MLAG device group, cable the local
        # port-channel interface to the pseudo port-channel interface on the
        # peer device.

        for tr_dev in self.group_members:
            tr_dev.interfaces[mlag_if_name].cable_peer = peer_mlag_dev.interfaces[
                peer_if_ame
            ]

        # for each of the remote devices, cable the local port-channel interface to
        # the pseudo port-channel on the transit-core.

        vlans_used = set()
        for r_dev in peer_mlag_dev.group_members:
            r_dev.interfaces[peer_if_ame].cable_peer = self.interfaces[mlag_if_name]
            vlans_used.update(r_dev.interfaces[peer_if_ame].profile.vlans_used())

        # Ensure that both sides of the mlag have the same allowed vlans.

        allowed_vlans = list(vlans_used)
        peer_mlag_dev.interfaces[peer_if_ame].profile.allowed_vlans = allowed_vlans
        rmt01.interfaces[peer_if_ame].profile.allowed_vlans = allowed_vlans
        rmt02.interfaces[peer_if_ame].profile.allowed_vlans = allowed_vlans

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
