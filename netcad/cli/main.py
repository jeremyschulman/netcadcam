import click

from netcad import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """NetCAD - a declarative approach to network lifecycle management"""
    pass


@cli.group("build")
def clig_build():
    """build subcommands ..."""


@cli.command(name='get')
def cli_get():
    """get required artifacts used by design"""


@cli.group(name='config')
def clig_config():
    """configure NetCAD project settings ..."""
    pass


@cli.command(name="design")
def clig_design():
    """design subcommands ..."""
    pass


@cli.command(name='init')
def cli_init():
    """initialize NetCAD project files"""


@cli.group('push')
def clig_push():
    """push subcommands ..."""
    pass
