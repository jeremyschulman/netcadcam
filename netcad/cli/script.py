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

        obj_data = ''
        if len(exc.args) > 1:
            from pprint import pformat as pp
            obj_data = '\n'.join([pp(obj) for obj in exc.args[1:]])

        sys.exit("ERROR: " + exc.args[0] + "\n" + obj_data)
