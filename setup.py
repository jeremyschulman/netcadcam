# -*- coding: utf-8 -*-
from setuptools import setup

packages = [
    "netcad",
    "netcad.arango",
    "netcad.cabling",
    "netcad.cli_netcad",
    "netcad.cli_netcad.cli_build",
    "netcad.cli_netcad.cli_get",
    "netcad.cli_netcad.cli_report",
    "netcad.config",
    "netcad.design_services",
    "netcad.device",
    "netcad.init",
    "netcad.jinja2",
    "netcad.jinja2.j2_filters",
    "netcad.jinja2.j2_funcs",
    "netcad.netbox",
    "netcad.netcam",
    "netcad.netcam.cli",
    "netcad.origin",
    "netcad.phy_port",
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
        "netcad = netcad.cli_netcad:script",
        "netcam = netcad.netcam.cli:script",
    ]
}

setup_kwargs = {
    "name": "netcad",
    "version": "0.4.0",
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
