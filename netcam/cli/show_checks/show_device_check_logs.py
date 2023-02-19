#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from pathlib import Path
import json

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device

from .find_check_services import find_check_services
from .filter_results import filter_results
from .show_log_table import show_log_table


def show_device_test_logs(console: Console, device: Device, optionals: dict):
    tcr_dir: Path = device.tcr_dir

    for check_svc in find_check_services(device, optionals):
        # if the test results file does not exist, it means that the tests were
        # not executed.  For now, silently skip.  TODO: may show User warning?

        check_svc_name = check_svc.get_name()

        results_file = tcr_dir.joinpath(f"{check_svc_name}.json")
        if not results_file.exists():
            continue

        results = json.load(results_file.open())

        if not (results := filter_results(results=results, optionals=optionals)):
            continue

        # display the results in a Table form.
        show_log_table(console, device, results_file.name, results)
