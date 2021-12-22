import click

from netcad import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    netcam - network automation 'manufacturing'
    """
    pass
