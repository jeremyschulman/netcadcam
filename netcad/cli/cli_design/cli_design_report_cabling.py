# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
from operator import attrgetter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click
from rich.table import Table
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, DeviceInterface
from netcad.device.interface_profile import InterfaceVirtual
from netcad.cabling.cable_plan import CablePlanner

from netcad.cli.main import clig_design_report
from netcad.cli.common_opts import opt_devices, opt_network
from netcad.cli.get_devices import get_devices

NOT_USED = "[grey]UNUSED[/grey]"
NOT_ASSIGNED = "[grey]N/A[/grey]"
MISSING = "[red]MISSING[/red]"
VIRTUAL = "[blue]virtual[/blue]"


def interface_profile_names(iface: DeviceInterface) -> Tuple[str, str]:
    if not iface.used:
        return NOT_USED, NOT_ASSIGNED

    if not (if_prof := iface.profile):
        return NOT_ASSIGNED, NOT_ASSIGNED

    if isinstance(if_prof, InterfaceVirtual):
        return if_prof.name, VIRTUAL

    if not (port_prof := if_prof.port_profile):
        return if_prof.name, MISSING

    return if_prof.name, port_prof.name


def report_cabling_per_device(device: Device):
    console = Console()

    if_cables = [
        interface for interface in device.interfaces.values() if interface.cable_peer
    ]

    if_cables.sort()

    # Populate the report table using this sorted collection of cables.

    table = Table(
        title=f"Device Cabling: {device.name}",
        show_header=True,
        header_style="bold magenta",
    )

    for column in [
        "Device",
        "Interface",
        "Profile",
        "Port",
        "Remote Port",
        "Remote Profile",
        "Remote Interface",
        "Remote Device",
        "Cable-ID",
    ]:

        table.add_column(column)

    for dev_if in if_cables:
        rmt_if = dev_if.cable_peer

        table.add_row(
            device.name,
            dev_if.name,
            *interface_profile_names(dev_if),
            *reversed(interface_profile_names(rmt_if)),
            rmt_if.name,
            rmt_if.device.name,
            # check either end, for the case of an MLAG.
            dev_if.label or rmt_if.label,
        )

    console.print(table)


def report_cabling_per_network(cabling: CablePlanner, network: str):
    console = Console()

    if not cabling.cables:
        console.print(f"[yellow]{network}: No cables.[/yellow]")
        return

    # orient each cable row (left-device, right-device) based on their sorting
    # property (User defined, or hostname by default)

    cables = [
        [cable[0], *sorted(cable[1], key=attrgetter("device"))]
        for cable in cabling.cables.items()
    ]

    # then sort the table based on the device-name, and interface sort-key

    cables.sort(key=lambda c: (c[1].device.name, c[1], c[2].device.name, c[2]))

    table = Table(
        title=f"Network Cabling: {network}",
        show_header=True,
        header_style="bold magenta",
    )

    for column in [
        "Device",
        "Interface",
        "Profile",
        "Port",
        "Remote Port",
        "Remote Profile",
        "Remote Interface",
        "Remote Device",
        "Cable-ID",
    ]:

        table.add_column(column)

    for cable_id, dev_if, rmt_if in cables:
        table.add_row(
            dev_if.device.name,
            dev_if.name,
            *interface_profile_names(dev_if),
            *reversed(interface_profile_names(rmt_if)),
            rmt_if.name,
            rmt_if.device.name,
            cable_id,
        )

    console.print(table)


@clig_design_report.command(name="cabling")
@opt_devices()
@opt_network()
@click.pass_context
def cli_design_report_cabling(
    ctx: click.Context, devices: Tuple[str], networks: Tuple[str]
):
    """report cabling between devices"""

    if devices:
        dev_objs = get_devices(device_list=devices)
        print(f"Reporting on {len(dev_objs)} devices ...")
        for dev_obj in dev_objs:
            report_cabling_per_device(dev_obj)

        return

    if networks:
        for network in networks:
            cabler: CablePlanner
            if not (cabler := CablePlanner.registry_get(name=network)):
                ctx.fail(f"No cabling found for network: {network}")
                return

            report_cabling_per_network(network=network, cabling=cabler)

        return

    ctx.fail("Missing option: --device or --network")
