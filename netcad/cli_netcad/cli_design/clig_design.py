from netcad.cli_netcad.main import cli
from netcad.init import loader

# -----------------------------------------------------------------------------
#
#                                  design
#
# -----------------------------------------------------------------------------


@cli.group(name="design")
def clig_design():
    """design list, report, ..."""
    pass


@clig_design.group(name="report")
def clig_design_report():
    """design report subcommands ..."""

    designs = loader.import_designs_packages()
    loader.run_designs(designs)
