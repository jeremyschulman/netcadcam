#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ..cli_netcam_main import cli


@cli.group(name="config")
def clig_config():
    """device configuration subcommands ..."""
    pass
