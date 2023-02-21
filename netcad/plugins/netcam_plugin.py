#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import TYPE_CHECKING

from netcad.device import Device

if TYPE_CHECKING:
    from netcam.dut import DeviceUnderTest
    from netcam.dcfg import AsyncDeviceConfigurable

from .plugins import Plugin, PluginProtocol

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["NetcamPlugin"]


class NetcamPlugin(Plugin):
    """
    Netcam plugins provide a "get device under test" instance for the purpose of
    executing checks on the operational state of the network.
    """

    class NetcamPluginModule(PluginProtocol):
        def plugin_get_dut(self, device: "Device") -> "DeviceUnderTest":
            """Obtain the DUT instance for a given Device instance"""

        def plugin_get_dcfg(self, device: "Device") -> "AsyncDeviceConfigurable":
            """Obtain the device configurable instance for a given Device intance"""

    _plugin_typeref = NetcamPluginModule
