#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import asyncio

from netcad.design import Design
from netcad.device import Device
from netcad.igather import igather

from .. import colorize
from .origin import NetboxTopologyOrigin


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

        if not rec:
            tasks[_create_missing(origin, device=device)] = hostname
        else:
            tasks[_check_existing(origin=origin, record=rec, device=device)] = hostname

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

    if not (origin_metadata := getattr(device, "origin_metadata")):
        device_role = origin.config.get("default_device_role")
        site = origin.config.get("default_site")
        if not all((device_role, site)):
            raise RuntimeError(
                "Missing netcad.origin.netbox.topology default values: "
                "[default_device_role, default_site], check config file."
            )
    else:
        topology_metadata = origin_metadata.get(origin.name)
        device_role = topology_metadata.get("device_role")
        site = topology_metadata.get("site")
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


async def _check_existing(origin: NetboxTopologyOrigin, record: dict, device: Device):
    """

    Parameters
    ----------
    origin:
        netbox origin instance

    record: dict
        The netbox device record

    device: Device
        The design device instance

    Returns
    -------
    """
    origin.log.info(f"{origin.log_origin}: {device.name}: device.{colorize.ok}")
    # TODO: need to validate that the device is not different than in design.
