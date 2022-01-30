#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import KeysView

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------


from netcad.device.device_type import DeviceType, DeviceTypeInterfaceSpec


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["NetboxOriginDeviceType"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class NetboxOriginDeviceType(DeviceType):
    def __init__(self, *vargs, **kwargs):
        super(NetboxOriginDeviceType, self).__init__(*vargs, **kwargs)
        self._if_name2obj = {
            iface["name"]: iface for iface in self.origin_spec["interfaces"]
        }

    # -------------------------------------------------------------------------
    #
    #                OriginDeviceType ABC Implementations
    #
    # -------------------------------------------------------------------------

    @property
    def device_type(self) -> str:
        return self.origin_spec["device_type"]["model"]

    @property
    def interface_names(self) -> KeysView:
        return self._if_name2obj.keys()

    def get_interface(self, if_name: str) -> DeviceTypeInterfaceSpec:
        if_obj = self._if_name2obj[if_name]
        return DeviceTypeInterfaceSpec(
            if_name=if_name,
            if_type=if_obj["type"]["value"],
            if_type_label=if_obj["type"]["label"],
        )
