from netcad.netcad_cli.main import cli
from netcad.init import loader


@cli.group("build")
def clig_build():
    """build configs, tests, ..."""

    designs = loader.import_designs_packages()
    loader.run_designs(designs)
