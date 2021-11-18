# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import sys
import os

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.logger import get_logger
from .main import cli


def script():
    try:
        cli()

    except Exception as exc:
        if debug_opt := os.getenv("NETCAD_DEBUG"):
            debug_opt = int(debug_opt)
            import traceback

            if debug_opt > 1:
                traceback.print_exc()
            else:
                traceback.print_tb(exc.__traceback__, limit=-1)

        obj_data = ""
        if len(exc.args) > 1:
            from pprint import pformat as pp

            obj_data = "\n".join([pp(obj) for obj in exc.args[1:]])

        log = get_logger()
        log.critical("ERROR: " + exc.args[0] + "\n" + obj_data)
        sys.exit(1)
