from typing import Optional, Dict, List

from pathlib import Path


g_config = dict()
g_netcad_config_file: Optional[Path] = None
g_netcad_checks_dir: Optional[Path] = None
g_netcad_templates_dir: Optional[Path] = None
g_netcad_project_dir: Optional[Path] = None
g_netcad_cache_dir: Optional[Path] = None
g_netcad_designs: Optional[Dict] = None

g_netcam_plugins: Optional[List[Dict]] = None
g_netcam_plugins_os_catalog: Optional[Dict[str, Dict]] = None

g_netcad_plugins: Optional[List[Dict]] = None
g_netcad_plugins_catalog: Optional[Dict[str, Dict]] = None

g_debug_level: Optional[int] = 0
g_userenv_design_names: Optional[List] = None
