#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import traceback
from pprint import pformat as pf

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.config import netcad_globals

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["format_exc_message", "debug_enabled"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def debug_enabled() -> bool:
    return bool(netcad_globals.g_debug_level)


def format_exc_message(exc: Exception) -> str:
    """
    This function uses the exception parameter to formulate a message that will
    be used to output debug information.  The content of the message is taken
    from the stacktrace and the exception args.

    The environment variable NETCAD_DEBUG=<n> is used to determine the depth of
    the stacktrace to output.  For example, if n=2 then the stacktrace depth is
    two frames.

    Parameters
    ----------
    exc: Exception
        The originating exception that is used to generate the debug message.

    Returns
    -------
    str - the debug message string
    """

    if debug_level := netcad_globals.g_debug_level:
        traceback.print_tb(exc.__traceback__, limit=-debug_level)

    obj_data = ""
    if len(exc.args) > 1:
        obj_data = "\n".join([pf(obj) for obj in exc.args[1:]])

    return "!-EXCEPTION-! " + exc.args[0] + "\n" + obj_data
