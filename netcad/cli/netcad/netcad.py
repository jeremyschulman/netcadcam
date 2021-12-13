# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import sys

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from .cli_netcad_main import cli
from netcad.debug import format_exc_message

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
        cli()

    except Exception as exc:
        exc_msg = format_exc_message(exc)
        log = get_logger()
        log.critical(exc_msg)
        sys.exit(1)
