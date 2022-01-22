#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from netcad.design import Design
from netcad.igather import as_completed
from .origin import NetboxTopologyOrigin


async def netbox_push_devices(origin: NetboxTopologyOrigin, design: Design):

    devices = dict()

    # -------------------------------------------------------------------------
    # fetch devices from netbox
    # -------------------------------------------------------------------------

    tasks = {origin.api.fetch_device(hostname=name): name for name in design.devices}

    async for coro, res in as_completed(tasks):
        hostname = tasks[coro]
        devices[hostname] = res

    breakpoint()
    x = 1
