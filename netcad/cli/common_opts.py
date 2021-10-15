import click

opt_devices = lambda **params: click.option(
    "-d",
    "--device",
    "devices",
    metavar="[NAME]",
    help="device hostname(s)",
    multiple=True,
    **params
)


opt_network = lambda **params: click.option(
    "-n",
    "--network",
    "networks",
    multiple=True,
    metavar="[NETWORK]",
    help="network(s)",
    **params
)
