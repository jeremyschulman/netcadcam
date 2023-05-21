#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import json
from typing import Tuple
from collections import Counter

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table, Text
from rich.console import Console

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design import Design
from netcad.checks import CheckStatus
from netcad.cli.keywords import color_pass_fail

from .find_check_services import find_check_services
from .filter_results import filter_results


def show_design_summary_table(
    console: Console, design: Design, optionals: dict, devices: Tuple[str]
):
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

    design_tc_counts = 0
    dev_cntrs = Counter()

    # if the User provided a filtered list of devices, then reduce the set of
    # all devices by those that they want to see.

    dev_objs = [
        dev
        for dev in design.devices.values()
        if not any((dev.is_pseudo, dev.is_not_managed))
    ]

    if devices:
        dev_objs = filter(lambda d: d.name in devices, dev_objs)

    for device in dev_objs:
        dev_cntrs.clear()

        for check_svc in find_check_services(device, optionals):
            # if the test results file does not exist, it means that the tests were
            # not executed.  For now, silently skip.  TODO: may show User warning?

            tc_name = check_svc.get_name()
            results_file = device.tcr_dir.joinpath(f"{tc_name}.json")
            if not results_file.exists():
                continue

            results = json.load(results_file.open())

            if not (results := filter_results(results=results, optionals=optionals)):
                continue

            tcr_cntrs = Counter(res["status"] for res in results)
            dev_cntrs.update(tcr_cntrs)

        dev_tc_counts = sum(dev_cntrs.values())
        design_tc_counts += dev_tc_counts

        table.add_row(
            device.name,
            color_pass_fail(dev_cntrs),
            Text(str(dev_tc_counts)),
            Text(str(dev_cntrs[CheckStatus.PASS]), style=CheckStatus.PASS.to_style()),
            Text(str(dev_cntrs[CheckStatus.FAIL]), style=CheckStatus.FAIL.to_style()),
            Text(str(dev_cntrs[CheckStatus.INFO]), style=CheckStatus.INFO.to_style()),
            Text(str(dev_cntrs[CheckStatus.SKIP]), style=CheckStatus.SKIP.to_style()),
        )

    table.title = Text(
        f"Design: {design.name}, Total Results: {design_tc_counts}", justify="left"
    )

    console.print("\n", table, "\n")
