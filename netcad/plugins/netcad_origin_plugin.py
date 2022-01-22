#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Dict, List

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design import Design

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

from .plugins import Plugin, PluginProtocol

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["NetcadOriginPlugin"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class _NetcadOriginServicePlugin(Plugin):
    class _PluginProtocol(PluginProtocol):
        def plugin_origin_push(self, design: Design):
            """Perform the 'push' action"""

    _plugin_typeref = _PluginProtocol


class NetcadOriginPlugin(Plugin):
    """
    Netcam plugins provide a "get device under test" instance for the purpose of
    executing checks on the operational state of the network.
    """

    def __init__(self, config: dict):
        super().__init__(config)

        if "services" not in self.config:
            raise RuntimeError(
                f'Missing required "service" list in netcad.origins.name={self.name}'
            )

        self.services = dict()

    def load(self):
        # load the origin package and call the plugin-init function; used to
        # setup any global config.
        super().load()

        # now import any packages supporting the design services.
        for svc_name, svc_pkg in self.config["services"].items():
            pg_cfg = dict(name=svc_name, package=svc_pkg)
            self.services[svc_name] = _NetcadOriginServicePlugin(config=pg_cfg)
            self.services[svc_name].load()

    @classmethod
    def init(cls, plugin_configs: List[Dict]) -> "NetcadOriginPluginCatalog":
        """
        Initialization function that is called when the netcad script is run
        with a command to interact with "origin" systems.  This function
        will load all of the User defined plugins so that they can be
        used during the script processing command, such as "push".

        Parameters
        ----------
        plugin_configs: List[Dict]
            From the User netcad configuration file, the list of
            netcad.origin objects.

        Returns
        -------
        Dict
            The catalog of plugins, key=plugin-name, value=plugin-object
        """

        catalog = dict()

        for or_id, config in enumerate(plugin_configs, start=1):
            pg_obj = cls(config=config)

            try:
                pg_obj.load()

            except Exception as exc:
                rt = RuntimeError(
                    f"Failed to load netcad.origin[{or_id}].name={pg_obj.name}: {str(exc)}"
                )
                rt.__traceback__ = exc.__traceback__
                raise rt

            catalog[pg_obj.name] = pg_obj

        return catalog


NetcadOriginPluginCatalog = Dict[str, Plugin]
