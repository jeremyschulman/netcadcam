import click

from netcad import __version__
from netcad.init import init
from netcad.config import loader


@click.group()
@click.version_option(version=__version__)
def cli():
    init()


@cli.group("build")
def clig_build():
    """build subcommands ..."""
    loader.import_networks()

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

@cli.group(name="config")
def clig_config():
    """configure netcad project settings ..."""
    pass


# -----------------------------------------------------------------------------
#
#                                  design
#
# -----------------------------------------------------------------------------


@cli.group(name="design")
def clig_design():
    """design subcommands ..."""
    loader.import_networks()


@clig_design.group(name="report")
def clig_design_report():
    """design report subcommands ..."""
    pass


@cli.command(name="init")
def cli_init():
    """initialize netcad project files"""


# -----------------------------------------------------------------------------
#
#                                   push
#
# -----------------------------------------------------------------------------


@cli.group("push")
def clig_push():
    """push subcommands ..."""
    pass
