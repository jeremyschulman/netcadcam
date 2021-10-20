# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Tuple
from pathlib import Path

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import click

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------


from netcad.cli.main import clig_audit

from netcad.cli.common_opts import opt_devices, opt_network


@clig_audit.command(name="devices")
@opt_devices()
@opt_network()
@click.option(
    "--tests-dir",
    help="test cases root-directory",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    default="tests",
)
def cli_audit_device(devices: Tuple[str], networks: Tuple[str], tests_dir: Path):
    """
        Execute device tests on live network
    \n\b
        This command will use the device test cases to validate the running state
        compared to the expected states defined by the tests.

    \f
        Parameters
        ----------
        devices
        networks
        tests_dir
    """
    pass
