#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from netcad.cli.netcad.cli_netcad_main import cli

# -----------------------------------------------------------------------------
#
#                                  design
#
# -----------------------------------------------------------------------------


@cli.group(name="show")
def clig_design_show():
    """show commands ..."""
    pass
