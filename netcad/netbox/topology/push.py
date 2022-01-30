#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from netcad.design import Design

from .origin import NetboxTopologyOrigin

from .push_devices import netbox_push_devices
from .push_interfaces import netbox_push_interfaces
from .push_cabling import netbox_push_cabling
from .push_lags import netbox_push_lags
from .push_iface_ipaddrs import netbox_push_interface_ipaddrs


async def plugin_origin_push(design: Design, **options):
    async with NetboxTopologyOrigin() as origin:
        await netbox_push_devices(origin, design)
        await netbox_push_interfaces(origin, design)
        await netbox_push_interface_ipaddrs(origin, design)
        await netbox_push_lags(origin, design)
        await netbox_push_cabling(origin, design)
