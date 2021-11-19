import click

from netcad import __version__
from netcad.init import init


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    Network Computer Aided Design (CAD)
    """
    init()


# -----------------------------------------------------------------------------
# get command
# -----------------------------------------------------------------------------


@cli.group(name="get")
def clig_get():
    """get required artifacts used by design"""


# -----------------------------------------------------------------------------
#
#                                  config
#
# -----------------------------------------------------------------------------


# @cli.group(name="config")
# def clig_config():
#     """configure netcad project settings ..."""
#     pass


@cli.command(name="init")
def cli_init():
    """initialize netcad project files"""
    pass


# -----------------------------------------------------------------------------
#
#                                   push
#
# -----------------------------------------------------------------------------


@cli.group("push")
def clig_push():
    """push subcommands ..."""
    pass
