import click

from netcad import __version__
from netcad.init import init, loader


@click.group()
@click.version_option(version=__version__)
def cli():
    init()


@cli.group("audit")
def clig_audit():
    """audit configs, network tests, ..."""
    pass


@cli.group("build")
def clig_build():
    """build configs, tests, ..."""
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
    """design report, ..."""
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
