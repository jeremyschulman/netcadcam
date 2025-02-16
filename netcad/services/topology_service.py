#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Callable, ClassVar, Any
from dataclasses import dataclass
from operator import attrgetter, itemgetter
from collections import Counter, defaultdict

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from rich.table import Table
from sqlalchemy.dialects.postgresql import Insert

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.checks import CheckStatus
from netcad.device import Device, DeviceInterface
from netcad.device.profiles import InterfaceL3

from netcad.feats.topology import TopologyDesignFeature
from netcad.feats.topology.checks.check_device_info import DeviceInformationCheck
from netcad.feats.topology.checks.check_interfaces import InterfaceCheck
from netcad.feats.topology.checks.check_cabling_nei import InterfaceCablingCheck
from netcad.feats.topology.checks.check_ipaddrs import IPInterfaceCheck
from netcad.feats.topology.checks.check_transceivers import TransceiverCheck
from netcam.db import db_tables
from .graph_query import GraphQuery
from .service_check import DesignServiceCheck
from .service_report import DesignServiceReport, color_pass_fail
from .design_service import DesignService
from .services_analyzer import ServicesAnalyzer

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class TopologyService(DesignService):
    """
    The purpose of the TopologyService class is to provide a service level view
    of the topology related to the set of interfaces that match the criteria
    defined in the config object passed to the constructor.

    Attributes
    ----------
    config : TopologyServiceConfig
        The configuration object that defines the service criteria.

    devices : set[Device]
        The set of devices that are part of this specific topology

    interfaces : set[DeviceInterface]
        The set of device interfaces that are part of this specific topology

    Graph Relationships:
    ---------------------
        service -> [s] -> Interface
        service -> [c] -> CheckCabling

        Device -> [d] -> Interface
        Device -> [s] -> Interface
        Device -> [c] -> DeviceInformationCheck

        Interface -> [c] -> each of the inteferface checks
        Interface.profile -> [s] -> Interface
        Interface.profile -> [d] -> IP Addr
        Interface.profile -> [s] -> IP Addr

    """

    # -------------------------------------------------------------------------
    # Service Configuration
    # -------------------------------------------------------------------------

    @dataclass
    class Config:
        """This class is used to configure the topology service."""

        # reference to the topology design feature
        topology_feature: TopologyDesignFeature

        # function used to match interfaces that should be included in the service
        # generally, this will be a function that checks the interface profile
        # attributes, like "is_network".  The example callable in that case could
        # be a simple lambda function like:
        #
        #       lambda ifp: ifp.is_network

        match_interface_profile: Callable

    # -------------------------------------------------------------------------
    # Service Check Types
    # -------------------------------------------------------------------------

    class CheckCabling(DesignServiceCheck):
        """
        This check serves to validate the cabling between two interfaces.  While
        there are two separate checks on a feature basis, this service level check
        creates a relationship between the two so that we can reason about the
        overall status of the cabling.
        """

        check_type: ClassVar[str] = "topology.cabling"
        msrd: Any = None

        def details(self):
            return self.msrd

    def __init__(self, *vargs, config: Config, **kwargs):
        super().__init__(*vargs, **kwargs)
        self.config = config
        self.devices: set[Device] = None
        self.interfaces: set[DeviceInterface] = None

        self.match_interfaces()

        if not self.interfaces:
            raise ValueError(f"No interfaces found for topology service: {self.name}")

    def match_interfaces(self) -> bool:
        """
        Find all interfaces in the topology that match the service search
        criteria.
        """

        self.interfaces = {
            interface
            for device in self.design.devices.values()
            if not device.is_pseudo
            for interface in device.interfaces.values()
            if interface.profile
            and self.config.match_interface_profile(interface.profile)
        }

        self.devices = set(if_obj.device for if_obj in self.interfaces)

    # --------------------------------------------------------------------------
    #
    #                            Design Graph
    #
    # --------------------------------------------------------------------------

    def build_design_graph(self, ai: ServicesAnalyzer):
        """
        This function is used to create the topology design graph relating
        devices to their respective interfaces.  The graph is directed from
        device to interfaces:
                (D) -[has]-> (I)
                (I.profile) -[is assigned to]> (I)
                (I.profile) -[has]-> (IP_addr)
        """
        for dev_obj in self.devices:
            ai.db.execute(
                Insert(db_tables.DeviceTable)
                .values(
                    name=dev_obj.name,
                    alias=dev_obj.alias,
                    os=dev_obj.os_name,
                    device_type=dev_obj.device_type,
                )
                .on_conflict_do_nothing(index_elements=["name"])
            )

            ai.db.commit()

            dev_rec = (
                ai.db.query(db_tables.DeviceTable).filter_by(name=dev_obj.name).first()
            )
            ai.db_obj_map[dev_obj] = dev_rec

            ai.add_design_node(dev_obj, kind_type="device", rec_id=dev_rec.id)

            # NOTE:  DO NOT create a service edge between the device and
            # interface because we do not want "any device error" cause the
            # service to report a failure.  The service should only fail if the
            # device interfaces have errors.

        self._build_design_interfaces(ai)

    def _build_design_interfaces(self, ai: ServicesAnalyzer):
        for if_obj in self.interfaces:
            dev_rec = ai.db_obj_map[if_obj.device]

            ai.db.execute(
                Insert(db_tables.InterfacesTable)
                .values(
                    name=if_obj.name,
                    desc=if_obj.desc,
                    profile=if_obj.profile.name,
                    device_id=dev_rec.id,
                )
                .on_conflict_do_nothing(index_elements=["device_id", "name"])
            )

            ai.db.commit()
            if_rec = (
                ai.db.query(db_tables.InterfacesTable)
                .filter_by(name=if_obj.name, device=dev_rec)
                .first()
            )
            ai.db_obj_map[if_obj] = if_rec

            # design edge between device and interface (only once)

            if ai.add_design_node(if_obj, kind_type="interface", rec_id=if_rec.id):
                ai.add_design_edge(if_obj.device, if_obj)

            # always add service edge between device and interface
            ai.add_service_edge(self, if_obj.device, if_obj)

            # design edge betwee the interface profile and the interface
            if ai.add_design_node(
                if_obj.profile,
                kind_type="interface.profile",
                profile=if_obj.profile.name,
                device=if_obj.device.name,
                if_name=if_obj.name,
            ):
                # if.profile -> Interface
                ai.add_design_edge(if_obj.profile, if_obj)

            # always add service edge between the service and the interface
            # object.
            ai.add_service_edge(self, self, if_obj)

            # always add service edge between interface profile and interface
            ai.add_service_edge(self, if_obj.profile, if_obj)

            # if there is an interface assigned to the profile, then add that
            # IP objec as a node in the graph child to the interface profile.

            if isinstance(if_obj.profile, InterfaceL3):
                if ai.add_design_node(if_obj.profile.if_ipaddr, kind_type="ipaddr"):
                    ai.add_design_edge(if_obj.profile, if_obj.profile.if_ipaddr)

                ai.add_service_edge(self, if_obj.profile, if_obj.profile.if_ipaddr)

    # --------------------------------------------------------------------------
    #
    #                             Results Graph
    #
    # --------------------------------------------------------------------------

    def build_results_graph(self, ai: ServicesAnalyzer):
        """
        This function is used to create the topology results graph relating the
        feature checks to the device and interface design nodes.
        """
        self._build_results_devices(ai)
        self._build_results_interfaces(ai)

    def _build_results_devices(self, ai: ServicesAnalyzer):
        """
        Associate the device-info check result to the device design node
        """

        for dev_obj in self.devices:
            check_obj = ai.results_map[dev_obj][DeviceInformationCheck.check_type_()][
                dev_obj.name
            ]
            ai.add_check_edge(self, dev_obj, check_obj)

    def _build_results_interfaces(self, ai: ServicesAnalyzer):
        """
        Associate each of the interface checks with the Interface design node.
        """
        if_check_types = [
            InterfaceCheck.check_type_(),
            IPInterfaceCheck.check_type_(),
            TransceiverCheck.check_type_(),
            InterfaceCablingCheck.check_type_(),
            # TODO: other checks, like lags?
        ]

        for if_obj in self.interfaces:
            for check_type in if_check_types:
                # if the interface does not have this specific check, for
                # example not all interfaces have transceivers, then we skip.

                if not (
                    if_check_obj := ai.results_map[if_obj.device][check_type].get(
                        if_obj.name
                    )
                ):
                    continue

                ai.add_check_edge(self, if_obj, if_check_obj)

    # -------------------------------------------------------------------------
    #
    #                             Checks
    #
    # -------------------------------------------------------------------------

    async def check(self, ai: ServicesAnalyzer):
        """Generate the service level checks"""
        self._check_cabling(ai)

    def _check_cabling(self, ai: ServicesAnalyzer):
        # create the top level cabling check node that will be the parent to
        # each of the individual interface cabling checks.

        top_node = self.CheckCabling()
        ai.add_service_check(self, top_node)

        # -----------------------------------------------------------------------------
        # first step is to filter the list of cabling to only those that could
        # be performing LLDP in this topology.  That means excluding virtual
        # interfaces, for example.
        # -----------------------------------------------------------------------------

        cabling = self.config.topology_feature.cabling

        def if_ok(if_obj: DeviceInterface) -> bool:
            return if_obj in self.interfaces and not if_obj.profile.is_virtual

        cables = [ends for ends in cabling.cables.values() if all(map(if_ok, ends))]

        # -----------------------------------------------------------------------------
        # create the 'topology interface peer check' results based on the
        # results of the individual interface cabling checks.
        # -----------------------------------------------------------------------------

        if_cable_check = InterfaceCablingCheck.check_type_()

        for if_a, if_b in cables:
            # TODO: not sure the checks are missing, the but measurement could
            #       be missing.  May need to account for that scenario.

            if_a_r = ai.results_map[if_a.device][if_cable_check][if_a.name]
            if_b_r = ai.results_map[if_b.device][if_cable_check][if_b.name]

            # check passes if for interface checks pass.

            ok = if_a_r.status == CheckStatus.PASS and if_b_r.status == CheckStatus.PASS
            ifp_r = self.CheckCabling(ok=ok)

            # -----------------------------------------------------------------
            # create the graph relationship between the service level check and
            # the device feature level checks.
            # -----------------------------------------------------------------

            ai.add_check_node(self, ifp_r)
            ai.add_check_edge(self, ifp_r, if_a_r)
            ai.add_check_edge(self, ifp_r, if_b_r)

            # add the cable-check node to the top-node for traveral later.
            ai.add_check_edge(self, top_node, ifp_r)

    # -------------------------------------------------------------------------
    #
    #                             Reports
    #
    # -------------------------------------------------------------------------

    def build_report(self, ai: ServicesAnalyzer, flags):
        self.report = DesignServiceReport(title=f"Topology Service Report: {self.name}")
        self._build_report_devices(ai, flags)

        pass_table, fail_table = self.build_report_interfaces_table(ai, flags)
        self.report.add("Interfaces", True, pass_table)

        if fail_table.rows:
            self.report.add("Interfaces", False, fail_table)

        self._build_report_cabling(ai)
        self._build_report_ipaddrs(ai, flags)

    def _build_report_cabling(self, ai: ServicesAnalyzer):
        # ---------------------------------------------------------------------
        # get the top level topology cabling check node to determine the
        # overall status of the cabling checks.
        # ---------------------------------------------------------------------

        svc_cable_node = (
            GraphQuery(ai.graph)(ai.nodes_map[self])
            .out_()
            .node(check_type=self.CheckCabling.check_type)
            .first()
        )

        # ---------------------------------------------------------------------
        # Cabling report
        # ---------------------------------------------------------------------

        if pass_c := svc_cable_node["pass_count"]:
            self.report.add("Cabling", True, {"count": pass_c})

        if fail_c := svc_cable_node["fail_count"]:
            self.report.add("Cabling", False, {"count": fail_c})

    def _build_report_devices(self, ai: ServicesAnalyzer, flags: dict):
        """
        For device checks, we only care about the directly associated results,
        and not the associated interface results.  This means that a device may
        be in a "FAIL" status because of the associated interfaces errors.  But
        we do not want to report that condition; only the condition of
        specifically device results.
        """

        pass_fail_c = Counter()

        table = Table("Status", "Device", "Model")

        for dev_obj in sorted(self.devices, key=attrgetter("name")):
            dev_node = ai.nodes_map[dev_obj]

            # find all the device specific checks (really only one right now,
            # but could be more in the future).

            pass_fail = (
                GraphQuery(ai.graph)(dev_node).out_().groupby(itemgetter("status"))
            )
            dev_fail = bool(pass_fail["FAIL"])
            pass_fail_c[not dev_fail] += 1

            # if the device passes, and we do not want to see details, then do
            # not add anything to the table.

            if not dev_fail and not flags.get("all_results"):
                continue

            table.add_row(
                color_pass_fail(not dev_fail), dev_obj.name, dev_obj.device_type
            )

        ok = pass_fail_c[False] == 0

        if flags.get("all_results") or table.rows:
            self.report.add("Devices", ok, table)
        else:
            self.report.add("Devices", ok, {"count": pass_fail_c[True]})

    def build_report_interfaces_table(
        self,
        ai: ServicesAnalyzer,
        flags,
    ) -> tuple[Table, Table]:
        """
        The "interfaces report" checks the interface design nodes for
        PASS/FAIL. If all are OK, then this report check passes.

        Returns
        -------
        pass_table, fail_table
        """

        pass_fail_nodes = defaultdict(list)
        fail_table = Table("Device", "Interface", "Desc", "Profile", "Logs")

        for if_obj in self.interfaces:
            if_node = ai.nodes_map[if_obj]
            pass_fail_nodes[if_node["fail_count"] == 0].append((if_obj, if_node))

        # ---------------------------------------------------------------------
        # create a table of failure interfaces
        # ---------------------------------------------------------------------

        for if_obj, if_node in pass_fail_nodes[False]:
            table = Table()

            check_nodes = (
                GraphQuery(ai.graph)(if_node).out_(service=self.name, kind="r").nodes
            )

            for check_obj in map(ai.nodes_map.inv.__getitem__, check_nodes):
                table.add_row(self.build_feature_logs_table(check_obj))

            fail_table.add_row(
                if_obj.device.name, if_obj.name, if_obj.desc, if_obj.profile.name, table
            )

        # ---------------------------------------------------------------------
        # if we do not want to see the details of the passing interfaces, then
        # just return the pass count as the "pass table".
        # ---------------------------------------------------------------------

        if not flags.get("all_results"):
            pass_table = {"count": len(pass_fail_nodes[True])}
            return pass_table, fail_table

        # ---------------------------------------------------------------------
        # if we are here, then we want to see the details of the passing
        # interfaces.
        # ---------------------------------------------------------------------

        pass_table = Table("Device", "Interface", "Desc", "Profile", "Logs")
        for if_obj, if_node in pass_fail_nodes[True]:
            table = Table()
            check_nodes = (
                GraphQuery(ai.graph)(if_node).out_(service=self.name, kind="r").nodes
            )
            for check_obj in map(ai.nodes_map.inv.__getitem__, check_nodes):
                table.add_row(self.build_feature_logs_table(check_obj))

            pass_table.add_row(
                if_obj.device.name, if_obj.name, if_obj.desc, if_obj.profile.name, table
            )

        return pass_table, fail_table

    def _build_report_ipaddrs(self, ai: ServicesAnalyzer, flags):
        # list of [(dev_obj, if_check)] for all IPInterfaceCheck results

        ipaddrs_checks = sorted(
            [
                (
                    if_obj.device,
                    ai.results_map[if_obj.device][IPInterfaceCheck.check_type_()][
                        if_obj.name
                    ],
                )
                for if_obj in self.interfaces
                if isinstance(if_obj.profile, InterfaceL3)
            ],
            # sorted by device.name, interface.name
            key=lambda i: (i[0].name, i[1].check_id),
        )

        table = Table("Status", "Device", "Interface", "IP Address")
        pass_fail_c = Counter()

        for dev_obj, if_check in ipaddrs_checks:
            pass_fail_c[if_check.status] += 1

            if if_check.status == "PASS" and not flags.get("all_results"):
                continue

            table.add_row(
                color_pass_fail(if_check.status == "PASS"),
                dev_obj.name,
                if_check.check_id,
                if_check.check.expected_results.if_ipaddr,
            )

        ok = pass_fail_c["FAIL"] == 0
        self.report.add(
            "IP Addresses", ok, table if table.rows else {"count": pass_fail_c["PASS"]}
        )
