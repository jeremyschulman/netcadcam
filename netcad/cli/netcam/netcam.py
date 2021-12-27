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
from netcad.init import init, init_plugings

# from netcad.netcam.loader import import_netcam_plugins

from .cli_netcam_main import cli


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


def script():
    """
    This function is the main entry point for the CLI tool when the User
    invokes the "netcam" command from the terminal.
    """
    try:
        init()
        init_plugings.import_netcam_plugins()
        cli()

    except Exception as exc:
        exc_msg = format_exc_message(exc)
        log = get_logger()
        log.critical(exc_msg)
        sys.exit(1)
