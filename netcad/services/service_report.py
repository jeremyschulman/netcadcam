from rich.table import Table
from rich.pretty import Pretty
from rich.text import Text, Style

from .service_check import DesignServiceCheck


class DesignServiceReport:
    did_pass = Text("PASS", Style(color="green"))
    did_fail = Text("FAIL", Style(color="red"))

    @classmethod
    def condition(cls, item):
        return cls.did_pass if item else cls.did_fail

    def __init__(self, title: str):
        self.table = Table(
            "Item", "Status", "Details", title=title, title_justify="left"
        )

    def add(self, item, check: DesignServiceCheck):
        self.table.add_row(item, self.condition(check), Pretty(check.details()))
