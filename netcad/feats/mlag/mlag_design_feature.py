#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Systeme Imports
# -----------------------------------------------------------------------------

from typing import TypeVar
from copy import copy

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from first import first

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.design.design_feature import DesignFeature

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .mlag_cabling import CableMLagsByCableId
from .mlag_device_group import DeviceMLagPairGroup

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["MLagDesignFeature", "MLagServiceLike"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class MLagDesignFeature(DesignFeature, registry_name="mlags"):
    CHECK_COLLECTIONS = []  # none for now

    def __init__(self, feature_name: str, **kwargs):
        # The cabling must be created first becasue the add_devices, which is
        # called by the superclass constructor, uses cabling

        self.cabling = CableMLagsByCableId(name=feature_name)

        # set up the design service with the User provided service name

        super(MLagDesignFeature, self).__init__(feature_name=feature_name, **kwargs)
        self.registry_add(name=feature_name, obj=self)
        self.check_collections = copy(self.__class__.CHECK_COLLECTIONS)

    def add_devices(self, *devices):
        super(MLagDesignFeature, self).add_devices(*devices)
        self.cabling.add_devices(*devices)

    @staticmethod
    def build_mlag(
        core_mlag_dev: DeviceMLagPairGroup,
        core_if_alias,
        core_if_profile,
        access_dev: Device,
        access_if_alias,
    ):
        for tr_dev in core_mlag_dev.group_members:
            tr_ifname = tr_dev.interfaces_map[core_if_alias]
            rmt_ifname = access_dev.interfaces_map[access_if_alias]
            tr_dev.interfaces[tr_ifname].cable_peer = access_dev.interfaces[rmt_ifname]
            access_dev.interfaces[rmt_ifname].cable_peer = core_mlag_dev.interfaces[
                tr_ifname
            ]

        core_mlag_dev.interfaces[tr_ifname].profile = core_if_profile()  # noqa
        core_mlag_dev.interfaces[tr_ifname].cable_peer = access_dev.interfaces[rmt_ifname]  # noqa


    @staticmethod
    def build_mlag2mlag(
        core_mlag_dev: DeviceMLagPairGroup,
        core_if_alias: str,
        core_if_profile,
        access_mlag_dev: Device,
        access_if_alias: str,
        access_if_profile,
    ):
        # get the first transit device so that we can obtain the actual transit
        # interface name from the alias.

        tr01 = first(core_mlag_dev.group_members)
        tr_if_map = tr01.interfaces_map
        tr_if_name = tr_if_map[core_if_alias]

        # get the remote device interface name from the alias.

        rmt01, rmt02 = access_mlag_dev.group_members
        rmt_if_map = rmt01.interfaces_map
        rmt_if_name = rmt_if_map[access_if_alias]

        # create profiles on each of the pseudo-mlag interfaces.

        core_mlag_dev.interfaces[tr_if_name].profile = core_if_profile()
        access_mlag_dev.interfaces[rmt_if_name].profile = access_if_profile()

        # cable the pseudo port-channels to each other.

        core_mlag_dev.interfaces[tr_if_name].cable_peer = access_mlag_dev.interfaces[
            rmt_if_name
        ]
        access_mlag_dev.interfaces[rmt_if_name].cable_peer = core_mlag_dev.interfaces[
            tr_if_name
        ]

        # for each of the transit devices, cable the local port-channel interface
        # to the pseudo port-channel interface on the remote device.

        for tr_dev in core_mlag_dev.group_members:
            tr_dev.interfaces[tr_if_name].cable_peer = access_mlag_dev.interfaces[
                rmt_if_name
            ]

        # for each of the remote devices, cable the local port-channel interface to
        # the pseudo port-channel on the transit-core.

        vlans_used = set()
        for r_dev in access_mlag_dev.group_members:
            r_dev.interfaces[rmt_if_name].cable_peer = core_mlag_dev.interfaces[tr_if_name]
            vlans_used.update(r_dev.interfaces[rmt_if_name].profile.vlans_used())

        # Ensure that both sides of the mlag have the same allowed vlans.

        allowed_vlans = list(vlans_used)
        access_mlag_dev.interfaces[rmt_if_name].profile.allowed_vlans = allowed_vlans
        rmt01.interfaces[rmt_if_name].profile.allowed_vlans = allowed_vlans
        rmt02.interfaces[rmt_if_name].profile.allowed_vlans = allowed_vlans

    def build(self):
        # run the build process on each of the MLag device groups so that the
        # concrete devices have their interface profiles created that match the
        # MLag device-group.

        for dev_group in filter(lambda _d: _d.is_mlag_group, self.devices):
            dev_group.build()

        # next run the cabling build so that the cable_peers are created so
        # that each of the concrete device interfaces are assgined for the
        # purposes of topology usage (such as peer interface descriptions,
        # VLANs, etc.)

        self.cabling.build()

    def validate(self):
        pass


MLagServiceLike = TypeVar("MLagServiceLike", MLagDesignFeature, DesignFeature)
