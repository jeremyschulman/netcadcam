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

from netcad.config import Environment
from netcad.netcad_cli.common_opts import opt_devices, opt_network
from .clig_test import clig_test

# -----------------------------------------------------------------------------
# Exports (none)
# -----------------------------------------------------------------------------

__all__ = []


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_test.command(name="devices")
@opt_devices()
@opt_network()
@click.option(
    "--tests-dir",
    help="location to store test-cases",
    type=click.Path(path_type=Path, resolve_path=True, exists=True, writable=True),
    envvar=Environment.NETCAD_TESTCASESDIR,
)
def cli_test_device(devices: Tuple[str], networks: Tuple[str], tests_dir: Path):
    """
    Execute tests against network devices.

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
