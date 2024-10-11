from pathlib import Path
import jinja2

from .rt_def_route_map import RouteIntentAction


class ActionCommunityDelete(RouteIntentAction):
    action = "permit"

    template = Path("rp/route_map_action_del_comm.jinja2")

    def __init__(self, community):
        super().__init__()
        self.community = community


class ActionCommunityAdd(RouteIntentAction):
    action = "permit"

    template = Path("rp/route_map_action_add_comm.jinja2")

    def __init__(self, community):
        super().__init__()
        self.community = community


class ActionCommunitySet(RouteIntentAction):
    action = "permit"

    template = Path("rp/route_map_action_set_comm.jinja2")

    def __init__(self, communities):
        super().__init__()
        self.communities = communities

    def community_list(self):
        return " ".join(map(str, self.communities))


class ActionPermit(RouteIntentAction):
    action = "permit"

    @jinja2.pass_context
    def render(self, ctx: jinja2.runtime.Context) -> str:
        return ""

    def __repr__(self):
        return "ActionPermit()"


class ActionDeny(RouteIntentAction):
    action = "deny"

    @jinja2.pass_context
    def render(self, ctx: jinja2.runtime.Context) -> str:
        return ""

    def __repr__(self):
        return "ActionDeny()"


class ActionSetPref(RouteIntentAction):
    action = "permit"

    template = Path("rp/route_map_action_set_pref.jinja2")

    def __init__(self, pref: int):
        super().__init__()
        self.pref = pref

    def __repr__(self):
        return f"ActionSetPref({self.pref})"
