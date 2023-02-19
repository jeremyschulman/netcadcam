#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Dict

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table, Text
from rich.console import Console
from rich.pretty import Pretty

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.checks import CheckStatus
from netcad.checks.check_result_log import CheckResultLogs


# TODO: remove this only when all of the DUT checkers are migrated over to the
#       new CheckResult mechanism.


def show_log_table(
    console: Console, device: Device, filename: str, results: List[Dict]
):
    table = Table(
        "Status",
        "Device",
        "Id",
        "Field",
        "Log",
        title=Text(f"Device: {device.name}\n   Test Logs: {filename}", justify="left"),
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )

    for result in results:
        if not (log_data := result["logs"]):
            log_data = result["measurement"]

        status = CheckStatus(result["status"])

        table.add_row(
            Text(status, style=status.to_style()),
            device.name,
            result["check_id"],
            result.get("field"),
            _pretty_dict_table(log_data),
        )

    console.print("\n", table, "\n")


def _pretty_dict_table(obj):
    # if given a string, just return the string.
    if isinstance(obj, str):
        return obj

    # otherwise, we will make a Table out of the object, depending on its
    # shape; list or dict

    table = Table(show_header=False, box=None)

    # if the obj is a dictionary, then make a pretty-table of key-value pairs.

    if isinstance(obj, dict):
        for key, value in obj.items():
            table.add_row(key, Pretty(value))

        return table

    if isinstance(obj[0], list):
        log_table = CheckResultLogs.parse_obj(obj)
        return log_table.pretty_table(table)

    return Pretty(obj)
