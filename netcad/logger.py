# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import logging
from functools import lru_cache

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.logging import RichHandler

# python logging format, defined here:
# https://docs.python.org/3/library/logging.html#logrecord-attributes

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["get_logger"]

# -----------------------------------------------------------------------------
#
#                                  CODE BEGINS
#
# -----------------------------------------------------------------------------

DEFAULT_LOG_FORMAT = ": %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %I:%M:%S(%p)"
DEFAULT_LOG_LEVEL = "INFO"


@lru_cache
def get_logger(show_path=False) -> logging.Logger:
    """
    Returns the python Logger used by NetCAD.

    Parameters
    ----------
    show_path: bool
        If enabled, will show the code location (filename:lineno) where the log
        was created.  Handy for debugging!

    Returns
    -------
    logging.Logger
    """
    logging.basicConfig(
        level=DEFAULT_LOG_LEVEL,
        format=DEFAULT_LOG_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                log_time_format=DEFAULT_DATE_FORMAT,
                show_path=show_path,
                markup=True,
            )
        ],
    )

    return logging.getLogger(__package__)
