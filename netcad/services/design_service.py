from typing import Any, TYPE_CHECKING

from netcad.checks import CheckResult

if TYPE_CHECKING:
    from .services_analyzer import ServicesAnalyzer


class DesignService:
    def __init__(self, design, name: str, owner: str, config: Any | None = None):
        self.design = design
        self.name = name
        self.owner = owner
        self.config = config
        self.failed: list[CheckResult] = list()

        self.design.services[name] = self

    def build(self, ai: "ServicesAnalyzer"):
        # add a root level service node to th graph.  This will be used for
        # root level analysis later.  Init the status to PASS.  It could be
        # updated to FAIL after the analysis is complete.

        ai.add_node(self, kind="s", service=self.name, status="PASS")

        # build the design aspects into the analysis graph
        self.build_design_graph(ai)

        # build the results aspects into the analysis graph
        self.build_results_graph(ai)

    def build_design_graph(self, ai: "ServicesAnalyzer"):
        pass

    def build_results_graph(self, ai: "ServicesAnalyzer"):
        raise NotImplementedError()

    async def check(self, ai: "ServicesAnalyzer"):
        raise NotImplementedError()
