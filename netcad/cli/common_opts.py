import click

opt_devices = lambda **params: click.option(
    "-h",
    "--device",
    "devices",
    metavar="[DEVICE-NAME]",
    help="device hostname(s)",
    multiple=True,
    **params
)


opt_network = lambda **params: click.option(
    "-d",
    "--design",
    "networks",
    multiple=True,
    metavar="[DESIGN]",
    help="design(s)",
    **params
)
