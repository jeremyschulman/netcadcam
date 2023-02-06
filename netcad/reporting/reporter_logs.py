#  Copyright (c) 2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import List, Optional
from functools import partial

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table, Text
from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.checks import CheckStatus, CheckResult

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["ReporterLogs"]


class ReporterLogItem(BaseModel):
    status: CheckStatus
    title: str
    message: str
    results: Optional[List[CheckResult]]

    def __lt__(self, other: "ReporterLogItem"):
        return self.status.to_flag() < other.status.to_flag()


class ReporterLogs(BaseModel):
    name: str = Field(..., description="The design service name")
    logs: List[ReporterLogItem] = Field(default_factory=list)

    def default_table(self) -> Table:
        title = f"Service: {self.name}, {len(self.logs)} logs"
        return Table(
            "Status",
            "Title",
            "Message",
            title=title,
            show_header=True,
            header_style="bold magenta",
            title_justify="left",
            show_lines=True,
        )

    def pretty_table(self, table: Optional[Table] = None) -> Table:
        table = table or self.default_table()

        for log in sorted(self.logs, key=lambda _l: _l.status.to_flag()):
            table.add_row(
                Text(log.status, style=log.status.to_style()),
                log.title,
                log.message,
            )

        return table

    def log(self, /, status, title: str, message: str, results: Optional[list] = None):
        self.logs.append(
            ReporterLogItem(
                status=status, title=title, message=message, results=results
            )
        )

    def __len__(self):
        return len(self.logs)

    def __getattr__(self, item):
        """
        Define the getattr oberload so the caller can invite the logging methods
        that map to the various status levels.

        Parameters
        ----------
        item: str
            The name of the logging level, for example "pass" or "fail"
        """
        return partial(self.log, CheckStatus(item))
