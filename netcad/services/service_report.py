#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from rich.table import Table
from rich.pretty import Pretty
from rich.text import Text, Style

from .service_check import DesignServiceCheck


def color_pass_fail(item):
    return (
        Text("PASS", Style(color="green")) if item else Text("FAIL", Style(color="red"))
    )


class DesignServiceReport:
    did_pass = Text("PASS", Style(color="green"))
    did_fail = Text("FAIL", Style(color="red"))

    @classmethod
    def condition(cls, item):
        return cls.did_pass if item else cls.did_fail

    def __init__(self, title: str):
        self.table = Table(
            "Item",
            "Status",
            "Details",
            title=title,
            title_justify="left",
            show_lines=True,
        )

    def add(self, item, check: DesignServiceCheck, details=None):
        if isinstance(details, Table):
            deets = details
        elif isinstance(check, DesignServiceCheck):
            deets = Pretty(check.details())
        elif details is not None:
            deets = Pretty(details)
        else:
            deets = None

        self.table.add_row(item, self.condition(check), deets)
