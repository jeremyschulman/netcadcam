#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import sys

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from netcad.debug import format_exc_message
from netcad.init import init, init_plugings, builtin_plugins
from .cli_netcad_main import cli

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def script():
    """
    This function is the main entry point for the CLI tool when the User
    invokes the "netcad" command from the terminal.
    """
    try:
        init()
        builtin_plugins.init_netcad_builtin_plugins()
        init_plugings.init_netcad_plugins()
        cli()

    except Exception as exc:
        exc_msg = format_exc_message(exc)
        log = get_logger()
        log.critical(exc_msg)
        sys.exit(1)
