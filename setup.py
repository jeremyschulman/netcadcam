# -*- coding: utf-8 -*-
from setuptools import setup

packages = [
    "netcad",
    "netcad.arango",
    "netcad.cabling",
    "netcad.config",
    "netcad.design_services",
    "netcad.device",
    "netcad.init",
    "netcad.jinja2",
    "netcad.jinja2.filters",
    "netcad.jinja2.funcs",
    "netcad.netbox",
    "netcad.netcad_cli",
    "netcad.netcad_cli.cli_audit",
    "netcad.netcad_cli.cli_build",
    "netcad.netcad_cli.cli_design",
    "netcad.netcad_cli.cli_get",
    "netcad.netcam_cli",
    "netcad.origin",
    "netcad.testing_services",
    "netcad.testing_services.cabling",
    "netcad.testing_services.device",
    "netcad.testing_services.interfaces",
    "netcad.testing_services.lags",
    "netcad.testing_services.mlags",
    "netcad.testing_services.transceivers",
    "netcad.testing_services.vlans",
    "netcad.vlan",
]

package_data = {"": ["*"]}

install_requires = [
    "Jinja2>=3.0.2,<4.0.0",
    "aiofiles>=0.7.0,<0.8.0",
    "click>=8.0.1,<9.0.0",
    "httpx>=0.19.0,<0.20.0",
    "more-itertools>=8.10.0,<9.0.0",
    "pydantic>=1.8.2,<2.0.0",
    "rich>=10.12.0,<11.0.0",
    "tenacity>=8.0.1,<9.0.0",
    "toml>=0.10.2,<0.11.0",
]

entry_points = {
    "console_scripts": [
        "netcad = netcad.netcad_cli:script",
        "netcam = netcad.netcam_cli:script",
    ]
}

setup_kwargs = {
    "name": "netcad",
    "version": "0.3.0",
    "description": "Network Configuration Database",
    "long_description": "# Network Configuration Database\n",
    "author": "Jeremy Schulman",
    "author_email": None,
    "maintainer": None,
    "maintainer_email": None,
    "url": None,
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "entry_points": entry_points,
    "python_requires": ">=3.8,<4.0",
}


setup(**setup_kwargs)
