#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design import Design
from netcad.device import DeviceInterface
from netcad.device import profiles
from netcad.igather import as_completed

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

    async for coro, res in as_completed(tasks):
        # bar.update(task_id=bar_task, advance=1)
        hostname = tasks[coro]
        # origin.log.info(f"{origin.log_origin}: DEVICE.ENSURE {hostname} - OK.")


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
