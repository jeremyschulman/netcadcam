# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Any

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import jinja2


@jinja2.pass_context
def j2_filter_render(ctx, obj: Any, to_render: str, **kwargs):
    meth = f"render_{to_render}"

    if call_meth := getattr(obj, meth, None):
        return call_meth(ctx, **kwargs)

    raise RuntimeError(f"object {str(obj)} does not support redner method: {meth}")
