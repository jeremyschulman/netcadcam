from typing import Optional, TypeVar
from collections import UserDict, defaultdict

from netcad.design import DesignFeature
from . import CommunityList
from .rt_def_policy import RoutePolicy
from .rt_def_route_map import RouteMap
from .rt_def_community import Community
from .rt_def_prefixlist import PrefixList

T = TypeVar("T")


class NamedUserDict(UserDict[str, T]):
    def add(self, item: T) -> T:
        self[item.name] = item
        return item


class RoutingPolicyDeviceContext:
    def __init__(self):
        self.route_maps = NamedUserDict[RouteMap]()
        self.communities = list()
        self.prefix_lists = list()

    def build(self):
        for rm in self.route_maps.values():
            for ri_intent in rm.data:
                if not ri_intent.seq:
                    ri_intent.seq = rm.seq
                    rm.seq += rm.seq_step

                if isinstance(ri_intent.match, PrefixList):
                    self.prefix_lists.append(ri_intent.match)
                elif isinstance(ri_intent.match, Community):
                    self.communities.append(ri_intent.match)
                elif isinstance(ri_intent.match, CommunityList):
                    self.communities.extend(ri_intent.match.data)
                else:
                    raise ValueError(f"Unknown match type: {type(ri_intent.match)}")

        self.prefix_lists.sort(key=lambda x: x.name)
        self.communities = sorted(set(self.communities), key=lambda x: (x.name, x.asn))


class RoutingPolicyDesignFeature(DesignFeature):
    def __init__(self, feature_name: Optional[str] = None, **kwargs):
        super().__init__(feature_name=feature_name or "routing_policy", **kwargs)
        self.policies = NamedUserDict[RoutePolicy]()

        # holds per-device rt_bgp policy context, key is the device alias, for
        # example "tr01"
        self.contexts = defaultdict(RoutingPolicyDeviceContext)

    def build(self):
        for ctx in self.contexts.values():
            ctx.build()
