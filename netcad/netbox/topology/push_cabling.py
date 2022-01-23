#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design import Design
from netcad.device import DeviceInterface
from netcad.igather import igather

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from .. import colorize
from .origin import NetboxTopologyOrigin

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["netbox_push_cabling"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


async def netbox_push_cabling(origin: NetboxTopologyOrigin, design: Design):
    await origin.fetch_interface_cabling()

    # --------------------------------------------------------------------
    # find the cabling in the design.  Each entry in the ds_cabling set is a
    # tuple that is the same key-form as the origin fetch.
    # --------------------------------------------------------------------

    ds_cabling = set()

    for dev in design.devices.values():
        iface: DeviceInterface

        for iface in filter(lambda _i: _i.cable_peer, dev.interfaces.used().values()):
            peer_iface = iface.cable_peer
            end_a = (iface.device.name, iface.name)
            end_b = (peer_iface.device.name, peer_iface.name)
            key = tuple(sorted((end_a, end_b)))
            ds_cabling.add(key)

    # --------------------------------------------------------------------
    # check for unexpected cabling in netbox that is not in the design
    # --------------------------------------------------------------------

    nb_keys = set(origin.cabling)
    if extra_keys := (nb_keys - ds_cabling):
        for each_key in extra_keys:
            origin.log.warning(f"{origin.log_origin}: unexpected cable: {each_key}")

    # --------------------------------------------------------------------
    # create push tasks
    # --------------------------------------------------------------------

    tasks = set()

    for cable_key in ds_cabling:
        nb_cable = origin.cabling.get(cable_key)
        tasks.add(
            _create_missing(origin, cable_key=cable_key, design=design)
            if not nb_cable
            else _show_existing(origin, cable_key=cable_key, design=design)
        )

    await igather(tasks)


# -----------------------------------------------------------------------------
#
#                              PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


async def _create_missing(
    origin: NetboxTopologyOrigin, cable_key: Tuple, design: Design
):

    (dev_a, ifname_a), (dev_b, ifname_b) = cable_key

    nb_intf_a = origin.interfaces[dev_a][ifname_a]
    nb_intf_b = origin.interfaces[dev_b][ifname_b]

    ds_intf_a = design.devices[dev_a].interfaces[ifname_a]
    ds_intf_b = design.devices[dev_b].interfaces[ifname_b]

    label = f"{ds_intf_a.device_ifname} --- {ds_intf_b.device_ifname}"

    post_data = dict(
        termination_a_type="dcim.interface",
        termination_a_id=nb_intf_a["id"],
        termination_b_type="dcim.interface",
        termination_b_id=nb_intf_b["id"],
        label=label,
    )

    res = await origin.api.post("/dcim/cables/", json=post_data)
    if res.is_error:
        # this likely means that the cable cannot be created because the
        # endpoints exist in another cable.  For now, just report the error to
        # the User so they can remediate.
        errmsg = f"{cable_key}: {res.text}"
        origin.log.error(f"{origin.log_origin}: cable.{colorize.failed}: {errmsg}")
        return

    res.raise_for_status()
    origin.cabling[cable_key] = res.json()
    origin.log.info(f"{origin.log_origin}: cable.{colorize.created}: {label}")


async def _show_existing(
    origin: NetboxTopologyOrigin, cable_key: Tuple, design: Design
):
    (dev_a, ifname_a), (dev_b, ifname_b) = cable_key

    ds_intf_a = design.devices[dev_a].interfaces[ifname_a]
    ds_intf_b = design.devices[dev_b].interfaces[ifname_b]
    label = f"{ds_intf_a.device_ifname} --- {ds_intf_b.device_ifname}"

    origin.log.info(f"{origin.log_origin}: cable.{colorize.ok}: {label}")
