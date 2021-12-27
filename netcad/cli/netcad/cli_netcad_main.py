#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import click

from netcad import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    netcad - network automation computer aided design
    """
    pass


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
