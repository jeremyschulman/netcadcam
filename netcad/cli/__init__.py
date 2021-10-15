import sys

from .main import cli
from . import cli_build_configs
from . import clI_design_report_interfaces


def script():
    try:
        cli()
    except RuntimeError as exc:
        sys.exit(exc.args[0])
