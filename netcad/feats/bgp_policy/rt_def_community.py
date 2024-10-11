from collections import UserList
from typing import Optional
from pathlib import Path
import jinja2


class Community:
    template = Path("rp/community.jinja2")
    match_template = Path("rp/route_map_match_community.jinja2")

    def __init__(self, asn: str, target: str, name: Optional[str] = None):
        self.asn = asn
        self.target = target
        self.name = name

    @jinja2.pass_context
    def render(self, ctx: jinja2.runtime.Context) -> str:
        template = ctx.environment.get_template(str(self.template))
        return template.render(community=self).rstrip()

    @jinja2.pass_context
    def match_render(self, ctx: jinja2.runtime.Context) -> str:
        template = ctx.environment.get_template(str(self.match_template))
        return template.render(community=self).rstrip()

    def __repr__(self):
        return f"Community({self.asn}:{self.target}) == {self.name}"

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.asn == other.asn
            and self.target == other.target
        )

    def __lt__(self, other):
        return (self.asn, self.target) <= (other.asn, other.target)

    def __hash__(self):
        return hash((self.asn, self.target))

    def __str__(self):
        return f"{self.asn}:{self.target}"


class CommunityList(UserList):
    match_template = Path("rp/route_map_match_community.jinja2")

    def __init__(self, community_list: list[Community], name: str):
        super().__init__(community_list)
        self.name = name
        for co in self.data:
            co.name = name

    @jinja2.pass_context
    def match_render(self, ctx: jinja2.runtime.Context) -> str:
        template = ctx.environment.get_template(str(self.match_template))
        return template.render(community=self).rstrip()
