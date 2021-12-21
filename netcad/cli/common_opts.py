import click

from netcad.config import netcad_globals

opt_devices = lambda **params: click.option(
    "-d",
    "--device",
    "devices",
    metavar="[DEVICE-NAME]",
    help="device hostname(s)",
    multiple=True,
    **params,
)


def unique_required_design_collection(ctx, param, value):
    # if the User provided values, then use these before any exported into the
    # enviornment.

    from_env = netcad_globals.g_userenv_design_names

    if not value and not from_env:
        raise click.exceptions.MissingParameter(
            message="design required, not found in enviornment or CLI",
            ctx=ctx,
            param=param,
        )

    # given the design name either provided by the CLI or in the User
    # enviornment, ensure that each of these design names are actually present
    # in the design configuration file.

    given_designs = list(dict.fromkeys(value)) if value else from_env

    missing = {
        name for name in given_designs if name not in netcad_globals.g_netcad_designs
    }
    if missing:
        mlist = ", ".join(missing)
        raise click.exceptions.BadParameter(
            message=f'Given design names are not found in configuration file: "{mlist}"',
            ctx=ctx,
            param=param,
        )

    return given_designs


opt_designs = lambda **params: click.option(
    "-D",
    "--design",
    "designs",
    multiple=True,
    metavar="[DESIGN]",
    help="design(s)",
    is_eager=True,
    callback=unique_required_design_collection,
    **params,
)

opt_design = lambda **params: click.option(
    "-D", "--design", "design", metavar="[DESIGN]", help="design", **params
)
