#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import json
from pathlib import Path
from collections import Counter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table, Text
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.device import Device
from netcad.checks import CheckStatus
from netcad.cli.keywords import color_pass_fail

from .find_check_services import find_check_services
from .filter_results import filter_results


def show_device_brief_table(console: Console, device: Device, optionals: dict):
    tcr_dir: Path = device.tcr_dir

    table = Table(
        "Test Cases",
        "Status",
        "Total",
        "Pass",
        "Fail",
        "Info",
        "Skip",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )

    dev_tc_count = 0
    for check_svc in find_check_services(device, optionals):
        # if the test results file does not exist, it means that the tests were
        # not executed.  For now, silently skip.  TODO: may show User warning?
        tc_name = check_svc.get_name()

        results_file = tcr_dir.joinpath(f"{tc_name}.json")
        if not results_file.exists():
            continue

        results = json.load(results_file.open())

        if not (results := filter_results(results=results, optionals=optionals)):
            continue

        tcr_cntrs = Counter(res["status"] for res in results)
        tcr_total = sum(tcr_cntrs.values())
        dev_tc_count += tcr_total

        table.add_row(
            tc_name,
            color_pass_fail(tcr_cntrs),
            Text(str(tcr_total)),
            Text(str(tcr_cntrs[CheckStatus.PASS]), style=CheckStatus.PASS.to_style()),
            Text(str(tcr_cntrs[CheckStatus.FAIL]), style=CheckStatus.FAIL.to_style()),
            Text(str(tcr_cntrs[CheckStatus.INFO]), style=CheckStatus.INFO.to_style()),
            Text(str(tcr_cntrs[CheckStatus.SKIP]), style=CheckStatus.SKIP.to_style()),
        )

    table.title = Text(
        f"Device: {device.name}, Total Results: {dev_tc_count}", justify="left"
    )

    console.print("\n", table)
