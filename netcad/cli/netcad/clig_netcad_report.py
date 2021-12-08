from netcad.cli.netcad.cli_netcad_main import cli

# -----------------------------------------------------------------------------
#
#                                  design
#
# -----------------------------------------------------------------------------


# @cli.group(name="design")
# def clig_design():
#     """design list, report, ..."""
#     pass


@cli.group(name="report")
def clig_design_report():
    """design report subcommands ..."""
    pass


def netcad_add_design_report(func):
    clig_design_report.add_command(func)
