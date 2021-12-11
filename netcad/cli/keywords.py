from rich.text import Text, Style


def markup_color(text, color):
    return f"[{color}]{text}[/{color}]"


def color_pass_fail(_cntrs):
    return (
        Text("PASSED!", style=Style(color="green"))
        if _cntrs["FAIL"] == 0
        else Text("FAILED!", style=Style(color="red"))
    )


NOT_USED = markup_color("unused", "yellow")
NOT_ASSIGNED = markup_color("N/A", "grey")
MISSING = markup_color("MISSING", "red]")
VIRTUAL = markup_color("virtual", "blue")
