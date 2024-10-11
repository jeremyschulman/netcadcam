from typing import Optional

from .rt_def_route_map import (
    RouteIntent,
    RouteMap,
    RouteIntentMatchers,
)


class RoutePolicy:
    def __init__(
        self,
        name: str,
        intents: list[RouteIntent],
        match: Optional[RouteIntentMatchers] = None,
    ):
        self.name = name
        self.intents = intents
        self.match = match

    def get_intent(self, route_map: RouteMap, seq=0) -> RouteIntent:
        """
        This function is used to retrieve the rt_bgp intent from the policy
        for the given route-map object.
        """
        for intent in self.intents:
            if intent.route_map == route_map.name:
                if seq:
                    intent.seq = seq

                if not intent.match:
                    intent.match = self.match

                return intent

        raise ValueError(
            f"No intent in policy {self.name} found for route-map {route_map.name}"
        )
