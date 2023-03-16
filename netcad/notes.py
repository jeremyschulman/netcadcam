#  Copyright (c) 2023 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, List, Union, Any, Callable
from datetime import datetime
from dataclasses import dataclass

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import maya

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["Notepad"]

# -----------------------------------------------------------------------------


@dataclass
class Note:
    obj: Any
    message: str
    expires: Optional[maya.MayaDT] = None


class Notepad:
    """
    This class is used to collect up "notepad" about the design, device, etc.
    """

    Note = Note

    def __init__(self, parent: Any, singature: Callable[[Any], str] = None):
        self.notes: List[Note] = list()
        self.parent = parent
        self.signature = singature or str

    def add_note(self, message: str, expires: Optional[Union[datetime, str]] = None):
        if isinstance(expires, str):
            expires_dt = maya.when(expires)
        elif isinstance(expires, datetime):
            expires_dt = maya.MayaDT(expires.timestamp())
        else:
            expires_dt = None

        self.notes.append(Note(obj=self.parent, message=message, expires=expires_dt))
