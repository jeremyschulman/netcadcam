import click

from netcad import __version__
from netcad.init import init


@click.group()
@click.version_option(version=__version__)
def cli():
    init()


@cli.group("build")
def clig_build():
    """build subcommands ..."""


# -----------------------------------------------------------------------------
# get command
# -----------------------------------------------------------------------------


@cli.group(name="get")
def clig_get():
    """get required artifacts used by design"""


# -----------------------------------------------------------------------------
# config subcommands
# -----------------------------------------------------------------------------


@cli.group(name="config")
def clig_config():
    """configure netcad project settings ..."""
    pass


# -----------------------------------------------------------------------------
# design subcommands
# -----------------------------------------------------------------------------


@cli.group(name="design")
def clig_design():
    """design subcommands ..."""
    pass


@clig_design.group(name="report")
def clig_design_report():
    """design report subcommands ..."""
    pass


@cli.command(name="init")
def cli_init():
    """initialize netcad project files"""


@cli.group("push")
def clig_push():
    """push subcommands ..."""
    pass
