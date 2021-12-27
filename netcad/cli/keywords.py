#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections import Counter

from rich.text import Text, Style


def markup_color(text, color):
    return f"[{color}]{text}[/{color}]"


def color_pass_fail(_cntrs: Counter):
    total = sum(_cntrs.values())

    if total == _cntrs["SKIP"]:
        return Text("SKPPED!", style=Style(color="grey50"))

    return (
        Text("PASSED!", style=Style(color="green"))
        if _cntrs["FAIL"] == 0
        else Text("FAILED!", style=Style(color="red"))
    )


NOT_USED = markup_color("unused", "yellow")
NOT_ASSIGNED = markup_color("N/A", "grey")
MISSING = markup_color("MISSING", "red")
VIRTUAL = markup_color("virtual", "blue")
