from typing import Optional
from pathlib import Path
from collections import UserList
import jinja2

from .rt_def_prefixlist import PrefixList
from .rt_def_community import Community


RouteIntentMatchers = Community | PrefixList


class RouteIntentAction:
    def __init__(self, *vargs, **kwargs):
        pass

    @jinja2.pass_context
    def render(self, ctx: jinja2.runtime.Context) -> str:
        template = ctx.environment.get_template(str(self.template))
        return template.render(action=self).rstrip()


class RouteIntent:
    def __init__(
        self,
        intent: str,
        action: RouteIntentAction,
        match: Optional[RouteIntentMatchers] = None,
        route_map: Optional[str] = None,
        seq: Optional[int] = 0,
    ):
        self.intent = intent
        self.match = match
        self.action = action
        self.route_map = route_map
        self.seq = seq


class RouteMap(UserList):
    template = Path("rp/route_map.jinja2")

    def __init__(
        self, name: str, data: Optional[list[RouteIntent]] = None, seq=10, seq_step=10
    ):
        super().__init__(data)
        self.name = name
        self.seq = seq
        self.seq_step = seq_step

    @jinja2.pass_context
    def render(self, ctx: jinja2.runtime.Context) -> str:
        template = ctx.environment.get_template(str(self.template))
        return template.render(route_map=self).rstrip()

    def __lt__(self, other: "RouteMap"):
        return self.name <= other.name
