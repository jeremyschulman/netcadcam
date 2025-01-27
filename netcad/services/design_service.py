# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Any, TYPE_CHECKING

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table
from rich.pretty import Pretty

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.checks import CheckResult

from .service_report import DesignServiceReport

if TYPE_CHECKING:
    from .services_analyzer import ServicesAnalyzer

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class DesignService:
    def __init__(
        self,
        design,
        name: str,
        owner: str,
        config: Any | None = None,
        is_subservice: bool = False,
    ):
        """
        DesignService constructor.

        Parameters
        ----------
        design: Design
            The design object.

        name: str
            The name of the service as it will be shown to the User.

        owner: str
            The owner of the service as it will be shown to the User.  Could
            also be used as a filter so that a User can find only services that
            they own.

        config: Any
            The specific configuration parameters for the design service.

        is_subservice: bool
            If True, then this service will not be shown to the User as part of
            show commands.

        """
        self.design = design
        self.name = name
        self.owner = owner
        self.config = config
        self.is_subservice = is_subservice

        # track the list of failed feature checks.
        self.failed: list[CheckResult] = list()

        # add this service to the set of design services.
        self.design.services[name] = self

        # initialize the design service status to PASS.  This value will be set
        # to "FAIL" should any element in the service be knownn to be "FAIL".
        self.status = "PASS"

        self.report: DesignServiceReport = None

    def build(self, ai: "ServicesAnalyzer"):
        # add a root level service node to th graph.  This will be used for
        # root level analysis later.  Init the status to PASS.  It could be
        # updated to FAIL after the analysis is complete.

        ai.add_node(
            self,
            kind="s",
            kind_type=self.__class__.__name__,
            service=self.name,
            pass_count=0,
            fail_count=0,
            status="PASS",
        )

        # build the design aspects into the analysis graph
        self.build_design_graph(ai)

        # build the results aspects into the analysis graph
        self.build_results_graph(ai)

    def build_design_graph(self, ai: "ServicesAnalyzer"):
        """
        This function is used to build the design graph for the service.  The
        design graph represents nodes-edges that are related to the design. For
        example, buidling nodes Devices and Interfaces and the relatioonship
        between the two.  The design graph nodes provides "anchors" for result
        nodes.  For example, all interface feature check results will be
        associated with its design Interface node.
        """
        pass

    def build_results_graph(self, ai: "ServicesAnalyzer"):
        pass

    def build_report(self, ai: "ServicesAnalyzer"):
        pass

    async def check(self, ai: "ServicesAnalyzer"):
        pass

    def build_features_report_table(self) -> Table:
        table = Table(
            "Device",
            "Check Type",
            "Check ID",
            "Status",
            title=f"Service: {self.name}, Feature check failures",
            title_justify="left",
        )

        for check in sorted(self.failed, key=lambda i: i.device):
            fail_logs = [log for log in check.logs.root if log[0] == "FAIL"]
            device = check.device
            check_id = check.check_id
            table.add_row(device, check.check.check_type, check_id, Pretty(fail_logs))

        return table
