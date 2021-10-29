import asyncio

from netcad.cli.main import cli
from netcad.init import loader

# -----------------------------------------------------------------------------
#
#                                  design
#
# -----------------------------------------------------------------------------


@cli.group(name="design")
def clig_design():
    """design report, ..."""
    modules = loader.import_networks()

    design_tasks = [
        getattr(mod, "design")()
        for mod in modules
        if hasattr(mod, "design") and asyncio.iscoroutinefunction(mod.design)
    ]

    async def run_design(tasks):
        await asyncio.gather(tasks)

    if design_tasks:
        asyncio.run(run_design(*design_tasks))


@clig_design.group(name="report")
def clig_design_report():
    """design report subcommands ..."""
    pass
