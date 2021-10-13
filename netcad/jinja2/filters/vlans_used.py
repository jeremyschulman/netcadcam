import typing as t

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import jinja2


@jinja2.pass_context
def j2_filter_vlans_used(ctx: jinja2.runtime.Context, obj: t.Any, scope="vlans"):
    return ""
