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
from netcad.logger import get_logger

from netcad.checks import (
    CheckInfoLog,
    CheckStatus,
    CheckPassResult,
    CheckFailResult,
    CheckSkipResult,
)
from netcad.checks.check_result_log import CheckResultLogs


_TCS_2_TRT = {
    CheckStatus.PASS: CheckPassResult,
    CheckStatus.FAIL: CheckFailResult,
    CheckStatus.INFO: CheckInfoLog,
    CheckStatus.SKIP: CheckSkipResult,
}


def _colorize_status(status):
    options = CheckStatus

    color = {
        options.PASS: "green",
        options.FAIL: "red",
        options.INFO: "blue",
        options.SKIP: "magenta",
    }.get(status)

    return f"[{color}]{status}[/{color}]"


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
        # r_tcr = _TCS_2_TRT.get(result["status"], CheckInfoLog)
        # log_msg = r_tcr.log_result(result)

        if not (log_data := result["logs"]):
            lgr = get_logger()
            lgr.warning("Device: %s, checks %s - convert to logs", device, filename)
            r_tcr = _TCS_2_TRT.get(result["status"], CheckInfoLog)
            log_data = r_tcr.log_result(result)

        table.add_row(
            _colorize_status(result["status"]),
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

    log_table = CheckResultLogs.parse_obj(obj)
    return log_table.pretty_table(table)
