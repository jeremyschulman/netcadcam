import sys
import os

from .main import cli
from . import cli_build_configs
from . import cli_design_report_interfaces
from . import cli_design_report_cabling


def script():
    try:
        cli()
    except RuntimeError as exc:
        if ("--debug" in sys.argv) or os.getenv("NETCAD_DEBUG"):
            import traceback

            traceback.print_exc()

        sys.exit("ERROR: " + exc.args[0])
