#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Systme Imports
# -----------------------------------------------------------------------------

import asyncio

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design import Design
from netcad.device import Device
from netcad.igather import igather

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from .. import colorize
from .origin import NetboxTopologyOrigin

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["netbox_push_devices"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


async def netbox_push_devices(origin: NetboxTopologyOrigin, design: Design):

    # -------------------------------------------------------------------------
    # fetch devices from netbox
    # -------------------------------------------------------------------------

    await origin.fetch_devices(design)

    # -------------------------------------------------------------------------
    # take action depending on whether or not the device(s) exist in Netbox
    # -------------------------------------------------------------------------

    tasks = dict()

    for hostname, rec in origin.devices.items():
        device = design.devices[hostname]
        task = (
            _update_existing(origin=origin, record=rec, device=device)
            if rec
            else _create_missing(origin, device=device)
        )
        tasks[task] = hostname

    await igather(tasks)


async def _create_missing(origin: NetboxTopologyOrigin, device: Device):
    """
    This function creates devices into Netbox that are not currently present.
    When creating a new netbox device, the following fields are required:
        * device_type (int)
        * device_role (int)
        * site (int)

    Parameters
    ----------
    origin:
        The netbox origin intance

    device: Device
        The design device that needs to be created in Netbox.
    """

    # -------------------------------------------------------------------------
    # Obtain the netbox device-type object from the device instance. this will
    # give us the device-type value we need when creating the new device record.
    # -------------------------------------------------------------------------

    nb_device_type_obj = device.device_type_spec.origin_spec
    device_type = nb_device_type_obj["device_type"]

    # -------------------------------------------------------------------------
    # Obtain the site and device-role information
    # -------------------------------------------------------------------------

    if not hasattr(device, "origin_metadata"):
        setattr(device, "origin_metadata", {})

    topology_metadata: dict = device.origin_metadata.get(origin.name)
    device_role = topology_metadata.setdefault(
        "device_role", origin.config.get("default_device_role")
    )
    site = topology_metadata.setdefault(
        "site", origin.config.get("default_device_site")
    )

    if not all((device_role, site)):
        raise RuntimeError(
            f"Device {device.name} missing origin_metadata.{origin.name}.[device_role, site]"
        )

    site_rec, devrole_rec = await asyncio.gather(
        origin.cache.fetch(
            client=origin.api, url="/dcim/sites/", params=dict(slug=site)
        ),
        origin.cache.fetch(
            client=origin.api, url="/dcim/device-roles/", params=dict(name=device_role)
        ),
    )

    # -------------------------------------------------------------------------
    # now create the device record in netbox
    # -------------------------------------------------------------------------

    res = await origin.api.post(
        "/dcim/devices/",
        json=dict(
            name=device.name,
            device_type=device_type["id"],
            device_role=devrole_rec["id"],
            site=site_rec["id"],
        ),
    )

    if res.is_error:
        origin.log.error(
            f"{origin.log_origin}: DEVICE.CREATE.FAIL: {device.name}: {res.text}"
        )
        return

    origin.devices[device.name] = res.json()
    origin.log.info(f"{origin.log_origin}: {device.name}: device.{colorize.created}")


async def _update_existing(origin: NetboxTopologyOrigin, record: dict, device: Device):
    """
    This function checks the existing netbox.device record against the design.
    The primary check is on the device-type value.  If this is not the same,
    then the User will see an ERROR log message so that they can manually
    remediate.

    This function will update the following fields:
        * device-role

    The origin.devices cache will be updated with the patch netbox device
    record.

    Parameters
    ----------
    origin:
        netbox origin instance

    record: dict
        The netbox device record

    device: Device
        The design device instance
    """

    # -------------------------------------------------------------------------
    # check for device-type match
    # -------------------------------------------------------------------------

    nb_dt = record["device_type"]
    ds_dt = device.device_type_spec.origin_spec["device_type"]

    if nb_dt["id"] != ds_dt["id"]:
        nb_name = nb_dt["slug"]
        ds_name = ds_dt["slug"]
        origin.log.error(
            f"{origin.log_origin}: {device.name}: "
            f"device.device-type mismatch: netbox/{nb_name} != design/{ds_name}"
        )
        return

    # -------------------------------------------------------------------------
    # check for device-role match, last check.  return if OK
    # -------------------------------------------------------------------------

    topo_meta: dict = device.origin_metadata.get(origin.name)
    match_dr = record["device_role"]["slug"] == topo_meta["device_role"]

    if match_dr:
        origin.log.info(f"{origin.log_origin}: {device.name}: device.{colorize.ok}")
        return

    # -------------------------------------------------------------------------
    # obtain the device-role record ID, required for the patch request
    # -------------------------------------------------------------------------

    devrole_rec = await origin.cache.fetch(
        client=origin.api,
        url="/dcim/device-roles/",
        params=dict(name=topo_meta["device_role"]),
    )

    # -------------------------------------------------------------------------
    # issue the patch request and update the origin cache
    # -------------------------------------------------------------------------

    patch_body = dict(
        device_type=nb_dt["id"],
        site=record["site"]["id"],
        device_role=devrole_rec["id"],
    )

    res = await origin.api.patch(f'/dcim/devices/{record["id"]}/', json=patch_body)
    res.raise_for_status()
    origin.devices[device.name] = res.json()

    origin.log.info(f"{origin.log_origin}: {device.name}: device.{colorize.updated}")
