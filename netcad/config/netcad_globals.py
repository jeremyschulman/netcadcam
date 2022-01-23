#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Optional, Dict, List, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from netcad.plugins import (
        NetcamPlugin,
        NetcadOriginPluginCatalog,
    )

g_config = dict()
g_netcad_config_file: Optional[Path] = None
g_netcad_checks_dir: Optional[Path] = None
g_netcad_templates_dir: Optional[Path] = None
g_netcad_project_dir: Optional[Path] = None
g_netcad_cache_dir: Optional[Path] = None
g_netcad_designs: Optional[Dict] = None

# -----------------------------------------------------------------------------
# Netcam driver plugins
# -----------------------------------------------------------------------------

g_netcam_plugins: Optional[List[Dict]] = None
g_netcam_plugins_os_catalog: Optional[Dict[str, "NetcamPlugin"]] = None

# -----------------------------------------------------------------------------
# Netcad design plugins
# -----------------------------------------------------------------------------

g_netcad_plugins: Optional[List[Dict]] = None
g_netcad_plugins_catalog: Optional[Dict[str, Dict]] = None

# -----------------------------------------------------------------------------
# Netcad origin plugins are used to communicate with external systems of record,
# for example "Netbox".
# -----------------------------------------------------------------------------

g_netcad_origin_plugins_catalog: Optional["NetcadOriginPluginCatalog"] = None

g_debug_level: Optional[int] = 0
g_userenv_design_names: Optional[List] = None
