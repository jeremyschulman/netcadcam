from typing import Optional
from pathlib import Path
from collections import UserList
import jinja2
from dataclasses import dataclass


@dataclass
class PrefixListItem:
    seq: int
    action: str
    prefix: str


class PrefixListIter:
    def __init__(self, prefixes, seq, step):
        self.prefixes = prefixes
        self.iter = iter(prefixes)
        self.seq = seq
        self.seq_step = step

    def __next__(self):
        prefix: str = next(self.iter)

        # default action is to permit if the User does not specify "deny"

        if prefix.startswith("deny"):
            action = "deny"
            prefix = prefix.split(" ", 1)[1]
        else:
            action = "permit"

        item = PrefixListItem(self.seq, action, prefix)
        self.seq += self.seq_step
        return item


class PrefixList(UserList):
    template = Path("rp/prefix_list.jinja2")
    match_template = Path("rp/route_map_match_prefix_list.jinja2")

    def __init__(
        self, prefixes, name: str, seq: Optional[int] = 5, seq_step: Optional[int] = 5
    ):
        super().__init__(prefixes)
        self.name = name
        self.seq = seq
        self.seq_step = seq_step

    @jinja2.pass_context
    def render(self, ctx: jinja2.runtime.Context) -> str:
        template = ctx.environment.get_template(str(self.template))
        return template.render(prefix_list=self).rstrip()

    @jinja2.pass_context
    def match_render(self, ctx: jinja2.runtime.Context) -> str:
        template = ctx.environment.get_template(str(self.match_template))
        return template.render(prefix_list=self).rstrip()

    def __iter__(self):
        return PrefixListIter(self.data, self.seq, self.seq_step)
