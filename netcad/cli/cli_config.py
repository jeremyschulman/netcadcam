from .main import cli


@cli.group(name="config")
def clig_config():
    """device configuration subcommands"""
