# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from ..common_opts import opt_devices, opt_designs
from ..device_inventory import get_devices_from_designs
from netcad.cli.netcad.clig_netcad_report import clig_design_report


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_design_report.command(name="ipaddrs")
@opt_designs(required=True)
@opt_devices()
def cli_design_report_interfaces(devices: Tuple[str], designs: Tuple[str], **flags):
    """
    report IP addresses used in design.

    \f
    Parameters
    ----------
    devices
    designs
    flags
    """
    log = get_logger()

    if not (
        dev_objs := get_devices_from_designs(designs=designs, include_devices=devices)
    ):
        log.error("No devices located in the given designs")
        return

    print(f"Checking {len(dev_objs)} devices ...")


# -----------------------------------------------------------------------------
#
#                               PRIVATE CODE BEGINS
#
# -----------------------------------------------------------------------------
