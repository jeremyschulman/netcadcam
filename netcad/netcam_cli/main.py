import click

from netcad import __version__
from netcad.init import init


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    Network Computer Aided Manufacturing (CAM)
    """
    init()
