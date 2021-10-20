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

from netcad.cli.main import clig_build
from netcad.cli.common_opts import opt_devices, opt_network


@clig_build.command(name="tests")
@opt_devices()
@opt_network()
@click.option(
    "--tests-dir",
    help="location to store configs",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    default="tests",
)
def cli_build_tests(
    devices: Tuple[str], networks: Tuple[str], configs_dir: Path, output_console: bool
):
    """
        Build device test cases to audit live network
    \n\b
        This command generates the device audit test cases.  These are collections
        of JSON files that indicate each of the specific tests that will be run
        against the live network.  The command to execute these tests is
        `netcad audit device` or `netcad audit network`.

    \f
        Parameters
        ----------
        devices
        networks
        configs_dir
        output_console

        Returns
        -------

    """
