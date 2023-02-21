#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.console import Console, Pretty
from rich.table import Table, Text

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device, DeviceInterface
from netcad.logger import get_logger

from netcad.cli.common_opts import opt_devices, opt_designs
from netcad.cli.device_inventory import get_devices_from_designs
from netcad.cli.clig_netcad_show import clig_design_show
from netcad.device.profiles import InterfaceLag

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_design_show.command(name="lags")
@opt_designs()
@opt_devices()
def cli_design_report_lags(devices: Tuple[str], designs: Tuple[str]):
    """
    show device lags usage

    \b
    The output includes the lag interface name, description, assigned profile, and
    associated physical interfaces.

    \f
    Parameters
    ----------
    designs: Tuple[str]
        A list of design names, as found in the User configuration file.

    devices: tuple[str]
        A list of device names, as would be found in the designated designs
    """
    log = get_logger()

    if not (
        dev_objs := get_devices_from_designs(designs=designs, include_devices=devices)
    ):
        log.error("No devices located in the given designs")
        return

    print(f"Checking {len(dev_objs)} devices ...")

    for each_dev in dev_objs:
        show_device_lags(each_dev)


def show_device_lags(device: Device):
    console = Console()
    table = Table(
        "LAG Interface",
        "Description",
        "Profile",
        "Member Interfaces",
        show_header=True,
        header_style="bold magenta",
        title=f"{device.name} LAG interfaces",
        title_justify="left",
    )

    def add_row(*columns):
        table.add_row(*columns)

    iface: DeviceInterface
    for iface in sorted(device.interfaces.used().values()):
        if not isinstance(if_prof := iface.profile, InterfaceLag):
            continue

        if_lag_members: list[DeviceInterface] = if_prof.if_lag_members

        if_desc = Text(iface.desc, "yellow") if if_prof.is_reserved else iface.desc
        add_row(
            iface.name,
            if_desc,
            if_prof.name,
            Pretty([if_lag_member.name for if_lag_member in if_lag_members]),
        )

    if not table.rows:
        return

    console.print(table, "\n")
