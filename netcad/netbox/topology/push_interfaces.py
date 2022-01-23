#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design import Design
from netcad.device import DeviceInterface
from netcad.device import profiles
from netcad.igather import igather

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from .. import colorize
from .origin import NetboxTopologyOrigin

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["netbox_push_interfaces"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


async def netbox_push_interfaces(origin: NetboxTopologyOrigin, design: Design):
    await origin.fetch_interfaces()
    tasks = dict()

    for device in design.devices.values():
        nb_dev_intfs = origin.interfaces[device.name]
        for interface in device.interfaces.values():
            task = (
                _create_missing(origin=origin, interface=interface)
                if not (nb_if_rec := nb_dev_intfs.get(interface.name))
                else _update_existing(
                    origin=origin, interface=interface, record=nb_if_rec
                )
            )
            tasks[task] = interface

    # execute all tasks wait for completion.
    await igather(tasks)


# -----------------------------------------------------------------------------
#
#                                 PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------


async def _create_missing(origin: NetboxTopologyOrigin, interface: DeviceInterface):
    """
    This function creates a netbox device.interface record based on the design
    information.

    To create a netbox.interface record, the following fields are required:
        * device (int) - the device ID
        * name (str) - the interface name
        * type (str) - the interface type

    Parameters
    ----------
    origin:
        netbox origin instance

    interface: DeviceInterface
        The interface to create in netbox
    """

    hostname = interface.device.name
    if_name = interface.name
    if not (if_profile := interface.profile):
        origin.log.error(
            f"{origin.log_origin}: {hostname}: interface missing profile: {if_name}"
        )
        return

    # -------------------------------------------------------------------------
    # map the interface profile type to a netbox interface type
    # -------------------------------------------------------------------------

    if isinstance(if_profile, profiles.InterfaceLag):
        if_type = "lag"
    elif isinstance(if_profile, profiles.InterfaceVirtual):
        if_type = "virtual"
    else:
        if_type = "other"
        origin.log.warning(
            f"{origin.log_origin}: {hostname}: interface unmapped profile type: {if_name}/{if_profile}"
        )

    # -------------------------------------------------------------------------
    # create the interface.  when OK update the origin interfaces cache
    # to store the new netbox interface record
    # -------------------------------------------------------------------------

    post_body = dict(
        device=origin.devices[hostname]["id"],
        name=if_name,
        type=if_type,
        description=interface.desc,
        enabled=interface.enabled,
    )

    res = await origin.api.post("/dcim/interfaces/", json=post_body)
    res.raise_for_status()
    origin.interfaces[hostname][if_name] = res.json()
    origin.log.info(
        f"{origin.log_origin}: {hostname}: interface.{colorize.created}: {if_name}"
    )


async def _update_existing(
    origin: NetboxTopologyOrigin, record: dict, interface: DeviceInterface
):
    """
    This function updates an existing Netbox interface record with the properties
    defined in the design device.interface object.  These attributes include the following:
        * description
        * enabled

    To patch a netbox.interface record, the following fields are required:
        * device (int) - the device ID
        * name (str) - the interface name
        * type (str) - the interface type

    """
    hostname = interface.device.name
    if_name = interface.name

    # determine if any change is needed.  if no change is needed then indicate
    # "ok" and return

    match_desc = record["description"] == interface.desc
    match_enable = record["enabled"] == interface.enabled

    if all((match_desc, match_enable)):
        origin.log.info(
            f"{origin.log_origin}: {hostname}: interface.{colorize.ok}: {if_name}"
        )
        return

    # fields for patch request

    patch_body = dict(
        device=record["device"]["id"], name=record["name"], type=record["type"]["value"]
    )

    patch_body["enabled"] = interface.enabled
    patch_body["description"] = interface.desc

    # execute the patch request.  if good, then store the updated netbox
    # interface record into the origin cache.  indicate "updated" to User.

    res = await origin.api.patch(f'/dcim/interfaces/{record["id"]}/', json=patch_body)
    res.raise_for_status()
    origin.interfaces[hostname][if_name] = res.json()
    origin.log.info(
        f"{origin.log_origin}: {hostname}: interface.{colorize.updated}: {if_name}"
    )
