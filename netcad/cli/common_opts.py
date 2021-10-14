import click


opt_devices = lambda **kwargs: click.option(
    "-d",
    "--device",
    "devices",
    metavar="[NAME]",
    help="device hostname(s)",
    multiple=True,
    **kwargs
)
