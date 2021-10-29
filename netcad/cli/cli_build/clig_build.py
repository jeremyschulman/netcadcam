import asyncio

from netcad.cli.main import cli
from netcad.init import loader


@cli.group("build")
def clig_build():
    """build configs, tests, ..."""

    modules = loader.import_networks()

    design_tasks = [
        mod.design()
        for mod in modules
        if hasattr(mod, "design") and asyncio.iscoroutinefunction(mod.design)
    ]

    async def run_design(tasks):
        await asyncio.gather(tasks)

    if design_tasks:
        asyncio.run(run_design(*design_tasks))
