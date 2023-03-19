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

__all__ = ["Notepad", "Note", "DateExpiryType", "SignatureCallbackType"]

# -----------------------------------------------------------------------------


SignatureCallbackType = Callable[[Any], str]
DateExpiryType = Union[datetime, str]


@dataclass
class Note:
    signatory: Any
    message: str
    expires: Optional[maya.MayaDT] = None
    _signature: Optional[Callable] = str

    def signature(self):
        return self._signature(self)


class Notepad:
    """
    This class is used to collect up "notepad" about the design, device, etc.
    """

    Note = Note

    def __init__(self, owner: Any):
        self.notes: List[Note] = list()
        self.owner = owner

    def add_note(
        self,
        signatory: Any,
        message: str,
        expires: Optional[DateExpiryType] = None,
        signature: Optional[SignatureCallbackType] = None,
    ):
        """
        This method adds a note to the notepad.

        Parameters
        ----------
        signatory:
            The object that originated the note.

        message:
            The note contents, as a string

        expires: optional
            If the note has an expiration date, then this value can be
            provided. If it is provided in either a datetime or string form,
            then it will be converted and stored as a MayaDT object so that it
            can be processed using the maya package.

        signature: optional
            If this callback function is provided, then it determiens how to
            represent the string-name of the signatory.  By default, this will
            be the str(signatory) value.
        """
        if isinstance(expires, str):
            expires_dt = maya.when(expires)
        elif isinstance(expires, datetime):
            expires_dt = maya.MayaDT(expires.timestamp())
        else:
            expires_dt = None

        self.notes.append(
            Note(signatory, message=message, expires=expires_dt, _signature=signature)
        )
