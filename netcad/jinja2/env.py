# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import typing as t

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

import jinja2

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .filters.vlans_used import j2_filter_vlans_used
from .filters.render import j2_filter_render
from .funcs.lookup import j2_func_lookup

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["get_env"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

_env_filters = {"vlans_used": j2_filter_vlans_used, "render": j2_filter_render}
_env_globals = {"lookup": j2_func_lookup}


class StringLoader(jinja2.BaseLoader):
    def get_source(
        self, environment: "jinja2.Environment", template: str
    ) -> t.Tuple[str, t.Optional[str], t.Optional[t.Callable[[], bool]]]:
        def uptodate() -> bool:
            return True

        return template, str(id(template)), uptodate


def _funcloader_get_source(source: str):
    if not isinstance(source, str):
        return None

    if source.startswith("str:"):
        return source[4:].strip()

    return None


def get_env(template_dirs):

    env = jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        loader=jinja2.ChoiceLoader(
            loaders=[
                jinja2.FunctionLoader(_funcloader_get_source),
                jinja2.FileSystemLoader(template_dirs),
            ]
        ),
    )

    env.filters.update(_env_filters)
    env.globals.update(_env_globals)

    return env
