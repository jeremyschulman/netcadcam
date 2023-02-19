#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import click

from netcad import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    netcam - network automation 'manufacturing'
    """
    pass
