import click

from netcfgdb import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    pass
