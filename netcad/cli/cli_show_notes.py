from typing import Tuple

from rich.table import Table
from rich.console import Console

from netcad.logger import get_logger
from netcad.cli.common_opts import opt_devices, opt_designs
from netcad.cli.device_inventory import get_devices_from_designs

from .clig_netcad_show import clig_design_show


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_design_show.command("notes")
@opt_designs()
@opt_devices()
def cli_show_notes(
    devices: Tuple[str],
    designs: Tuple[str],
):
    """
    show design notes
    """
    log = get_logger()

    if not (
        dev_objs := get_devices_from_designs(designs=designs, include_devices=devices)
    ):
        log.error("No devices located in the given designs")
        return

    table = Table(
        "Entity",
        "Message",
        "Expires",
        show_header=True,
        header_style="bold magenta",
        title_justify="left",
        title_style="bold",
    )

    # -------------------------------------------------------------------------
    # Design Level Notes
    # -------------------------------------------------------------------------
    # TODO

    # -------------------------------------------------------------------------
    # Design Service Level Notes
    # -------------------------------------------------------------------------
    # TODO

    # -------------------------------------------------------------------------
    # Device Interface Notes
    # -------------------------------------------------------------------------

    for dev in dev_objs:
        for if_obj in dev.interfaces.values():
            for note in if_obj.notepad.notes:
                exp_on = note.expires.slang_time() if note.expires else ""
                table.add_row(if_obj.notepad.signature(note.obj), note.message, exp_on)
        table.add_section()

    if not table.rows:
        print("No notes.")
        return

    console = Console()
    console.print(table)
