#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections import defaultdict


from netcad.design import Design
from netcad.device import DeviceInterface
from netcad.device.profiles import InterfaceL3, InterfaceIsLoopback
from netcad.ipam import AnyIPInterface
from netcad.igather import igather

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from .. import colorize
from .origin import NetboxTopologyOrigin

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["netbox_push_interface_ipaddrs"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


async def netbox_push_interface_ipaddrs(origin: NetboxTopologyOrigin, design: Design):
    await origin.fetch_ipaddrs()

    # key1=hostname, key2=ip-address(obj), value=DeviceInterface
    design_ipaddrs = defaultdict(dict)

    for dev in design.devices.values():
        for iface in dev.interfaces.used().values():
            if isinstance(iface.profile, InterfaceL3) and (
                if_ipaddr := iface.profile.if_ipaddr
            ):
                design_ipaddrs[dev.name][if_ipaddr] = iface

    # -------------------------------------------------------------------------
    # create the set of tasks to execute for the push action
    # -------------------------------------------------------------------------

    tasks = dict()

    for dev in design.devices.values():
        nb_ips = origin.ipaddrs[dev.name]
        ds_ips = design_ipaddrs[dev.name]
        for ip_obj, iface_obj in ds_ips.items():
            task = (
                _create_missing(origin=origin, if_ipaddr=ip_obj, interface=iface_obj)
                if not (nb_ip_rec := nb_ips.get(str(ip_obj)))
                else _update_existing(
                    origin=origin,
                    if_ipaddr=ip_obj,
                    interface=iface_obj,
                    record=nb_ip_rec,
                )
            )

            tasks[task] = (iface_obj, ip_obj)

    # execute tasks
    await igather(tasks)


# -----------------------------------------------------------------------------
#
#                              PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


async def _create_missing(
    origin: NetboxTopologyOrigin, if_ipaddr: AnyIPInterface, interface: DeviceInterface
):
    """
    This function creates a new netbox ip-address record bound to the given
    itnerface. Upon success, the new ip-address record is stored in the origin
    ipaddrs cache.

    Parameters
    ----------
    origin:
        netbox origin instance

    if_ipaddr: AnyIPInterface
        The IP interface object (from the ipaddress module)

    interface: DeviceInterface
        The device interface to which the IP will be bound

    """
    hostname = interface.device.name
    if_name = interface.name
    ip_addr = str(if_ipaddr)

    nb_if_rec = origin.interfaces[hostname][if_name]
    desc = f"{interface.device_ifname}:{interface.desc}"
    post_body = dict(
        address=ip_addr,
        assigned_object_type="dcim.interface",
        assigned_object_id=nb_if_rec["id"],
        description=desc,
    )

    if isinstance(interface.profile, InterfaceIsLoopback):
        post_body["role"] = "loopback"

    res = await origin.api.post("/ipam/ip-addresses/", json=post_body)
    res.raise_for_status()
    origin.ipaddrs[hostname][ip_addr] = res.json()
    origin.log.info(
        f"{origin.log_origin}: {hostname}: {if_name}: ip-address.{colorize.created}: {ip_addr}"
    )


async def _update_existing(
    origin: NetboxTopologyOrigin,
    if_ipaddr: AnyIPInterface,
    interface: DeviceInterface,
    record: dict,
):
    hostname = interface.device.name
    if_name = interface.name
    ip_addr = str(if_ipaddr)

    # check to see if the ip-address is assigned to the interface as expected.

    asgn_if_id = record["assigned_object_id"]
    nb_if_rec = origin.interfaces[hostname][interface.name]
    if asgn_if_id == nb_if_rec["id"]:
        origin.log.info(
            f"{origin.log_origin}: {hostname}: {if_name}: ip-address.{colorize.ok}: {ip_addr}"
        )
        return

    # TODO: need to handle the IP address -> interface re-assignment use-case.
    origin.log.warning(
        f"{origin.log_origin}: {hostname}: {if_name}: ip-address.{colorize.updated}: {ip_addr} (TODO)"
    )
