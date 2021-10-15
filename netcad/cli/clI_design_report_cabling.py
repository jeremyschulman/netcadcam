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


from .main import clig_design_report
from .common_opts import opt_devices
from .get_devices import get_devices


@clig_design_report.command(name="cabling")
@opt_devices(required=True)
def cli_design_report_cabling(devices: Tuple[str]):
    """report device interface cabling"""

    dev_objs = get_devices(device_list=devices)
    print(f"Checking {len(dev_objs)} devices ...")
