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


def unique_set(ctx, param, value):
    return set(value)


opt_designs = lambda **params: click.option(
    "-D",
    "--design",
    "designs",
    multiple=True,
    metavar="[DESIGN]",
    help="design(s)",
    callback=unique_set,
    **params
)

opt_design = lambda **params: click.option(
    "-D", "--design", "design", metavar="[DESIGN]", help="design", **params
)
