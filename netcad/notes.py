#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, List, Union
from datetime import date
from collections import UserList

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import maya
from pydantic import BaseModel, validator
from rich.table import Table
from rich.text import Text, Style

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["DesignNote", "DesignNotes"]


class DesignNote(BaseModel):
    date_start: Union[date, str]
    date_end: Optional[Union[date, str]]
    message: str

    @validator("date_start", pre=True)
    def _date_start(cls, v):
        return maya.when(v).date if isinstance(v, str) else v

    @validator("date_end", pre=True)
    def _date_end(cls, v):
        return maya.when(v).date if isinstance(v, str) else v

    def __lt__(self, other: "DesignNote"):
        return self.date_start < other.date_start


class DesignNotes(UserList, List[DesignNote]):
    def __init__(self):
        super().__init__()
        # backref to the design instance, set in the Design.__init__ method.
        self.design = None

    def table(self):
        if not (c_notes := len(self.data)):
            return

        title = (
            Text(
                f"Design Notes for '{self.design.name}'",
                style=Style(color="yellow"),
                justify="left",
            )
            + f" ({c_notes})"
        )

        table = Table(
            "Date",
            "Message",
            "End-Date",
            title=title,
            show_header=True,
            header_style="bold magenta",
        )

        for note in sorted(self.data):
            table.add_row(str(note.date_start), note.message, str(note.date_end or ""))

        return table
