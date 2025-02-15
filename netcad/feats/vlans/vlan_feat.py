#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Set, Optional, MutableMapping, TypeVar
from itertools import filterfalse
from operator import attrgetter
from collections import UserDict
from functools import lru_cache

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.design import DesignFeature

# -----------------------------------------------------------------------------
# Module Private Imports
# -----------------------------------------------------------------------------

from .vlan_profile import VlanProfile
from .vlan_ds_config import VlanDesignServiceConfig

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "VlansDesignFeature",
    "DeviceVlanDesignFeature",
    "DeviceVlanDesignServiceLike",
]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class DeviceVlanDesignFeature(DesignFeature):
    """
    The "Device Vlan" design service is used to manage the vlans on a per-device
    basis. This sevice, while all design features mataining a list of associated
    devices, has only one device.
    """

    def __init__(
        self,
        device: Device,
        config: VlanDesignServiceConfig,
        check_collections,
        feature_name: Optional[str] = "vlans",
    ):
        super().__init__(feature_name=feature_name)
        self.device = device
        self.check_collections = check_collections
        self.add_devices(device)
        self.alias_names = dict()
        self.config = config

    @lru_cache
    def all_vlans(self) -> List[VlanProfile]:
        """
        Returns a sorted list of VlanProfiles that are used by this speific
        device.

        Returns
        -------
        list - as described.
        """

        all_vlans: Set[VlanProfile] = set()
        interfaces = self.device.interfaces

        for if_name, iface in interfaces.used().items():
            if not (vlans_used := getattr(iface.profile, "vlans_used", None)):
                continue

            all_vlans.update(vlans_used())

        return sorted(all_vlans, key=attrgetter("vlan_id"))

    # -------------------------------------------------------------------------
    # Design Service required methods
    # -------------------------------------------------------------------------

    def build(self):
        self.all_vlans.cache_clear()
        _ = self.all_vlans()

    def validate(self):
        pass


DeviceVlanDesignServiceLike = TypeVar(
    "DeviceVlanDesignServiceLike", DeviceVlanDesignFeature, DesignFeature
)


class VlansDesignFeature(
    DesignFeature, UserDict, MutableMapping[Device, DeviceVlanDesignFeature]
):
    """
    The VlansDesignFeature enables a Designer to manage the arrangement and
    behavior of the VlanProfiles used by a design.  A device-specific design
    service is also created & associated to devices as they are added to the
    VlansDesignFeature.

    The VlansDesignFeature subclasses UserDict where each key is the Device
    instance and the value is the per-device Vlan design service.
    """

    # The per-device VLAN service class.  By default, will be the class defined
    # above.  A Designer may wish to subclass something different.

    device_vlan_service = DeviceVlanDesignFeature

    def __init__(
        self,
        feature_name: Optional[str] = "vlans",
        device_service_name: Optional[str] = "vlans",
        config: Optional[VlanDesignServiceConfig] = None,
        **kwargs,
    ):
        """
        Initialize the design level Vlan features.

        Parameters
        ----------
        name:
            The Designer designated name for this specific instance of the Vlans
            service.  By default, this value will be "design_vlans".

        device_service_name:
            The per-device specific vlan design service name.  By default, this
            value is "vlans".

        config:
            The Vlan design service configuration settings.  If None is
            provided, then a configuration instance is created with the default
            settings.
        """
        super().__init__(feature_name=feature_name, **kwargs)
        self._device_service_name = device_service_name
        self.config = config or VlanDesignServiceConfig()

    def add_devices(
        self, *devices: Device, config: Optional[VlanDesignServiceConfig] = None
    ) -> "VlansDesignFeature":
        """
        Add the list of Device instances to the VlanDesignService.  As a result
        each device will also be associated with the `device_vlan_service` class
        instance that allows for the device-specific arranngement of Vlans.

        Parameters
        ----------
        devices:
            List of Device instances

        config: optional
            The Vlan design service config instance to use for this device;
            could be different from the design service instance.  If not
            provided, then the design service config instance is used.

        Returns
        -------
        self instance for method-chaning
        """
        super().add_devices(*devices)

        for each_dev in filterfalse(lambda d: d in self.data, devices):
            self[each_dev] = self.device_vlan_service(
                feature_name=self._device_service_name,
                device=each_dev,
                check_collections=self.check_collections,
                config=config or self.config,
            )

        return self

    def build(self) -> "VlansDesignFeature":
        """
        Runs the vlan service build process on each associated device.

        Returns
        -------
        self for method-chaning
        """

        for each_dev in self.data.values():
            each_dev.build()

        return self

    def validate(self):
        """No validation action performed"""
        pass
