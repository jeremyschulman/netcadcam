# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.origin import Origin

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["OriginNetbox"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

from .netbox_origin_devicetype import NetboxOriginDeviceType


class OriginNetbox(Origin):
    package = __package__
    register_name = "netbox"
    device_type = NetboxOriginDeviceType
