import click

opt_devices = lambda **params: click.option(
    "-d",
    "--device",
    "devices",
    metavar="[DEVICE-NAME]",
    help="device hostname(s)",
    multiple=True,
    **params
)


opt_designs = lambda **params: click.option(
    "-D",
    "--design",
    "designs",
    multiple=True,
    metavar="[DESIGN]",
    help="design(s)",
    **params
)

opt_design = lambda **params: click.option(
    "-D", "--design", "design", metavar="[DESIGN]", help="design", **params
)
