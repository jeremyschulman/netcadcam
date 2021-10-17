import sys
import os

from .main import cli


def script():
    try:
        cli()
    except RuntimeError as exc:
        if ("--debug" in sys.argv) or os.getenv("NETCAD_DEBUG"):
            import traceback

            traceback.print_exc()

        sys.exit("ERROR: " + exc.args[0])
