#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from netcad.design import Design

from .origin import NetboxTopologyOrigin

from .push_devices import netbox_push_devices
from .push_interfaces import netbox_push_interfaces
from .push_cabling import netbox_push_cabling
from .push_lags import netbox_push_lags
from .push_ipaddrs import netbox_push_interface_ipaddrs


async def plugin_origin_push(design: Design):
    origin = NetboxTopologyOrigin()

    await netbox_push_devices(origin, design)
    await netbox_push_interfaces(design)
    await netbox_push_cabling(design)
    await netbox_push_lags(design)
    await netbox_push_interface_ipaddrs(design)
