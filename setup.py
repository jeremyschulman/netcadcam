# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from setuptools import setup

packages = [
    "netcad",
    "netcad.cabling",
    "netcad.checks",
    "netcad.cli",
    "netcad.cli.cli_get",
    "netcad.cli.netcad",
    "netcad.cli.netcam",
    "netcad.config",
    "netcad.design_services",
    "netcad.device",
    "netcad.init",
    "netcad.jinja2",
    "netcad.jinja2.j2_filters",
    "netcad.jinja2.j2_funcs",
    "netcad.netbox",
    "netcad.netcam",
    "netcad.origin",
    "netcad.phy_port",
    "netcad.topology",
    "netcad.vlan",
]

package_data = {"": ["*"]}

install_requires = [
    "Jinja2>=3.0.2,<4.0.0",
    "aiofiles>=0.7.0,<0.8.0",
    "click>=8.0.1,<9.0.0",
    "httpx>=0.19.0,<0.20.0",
    "maya>=0.6.1,<0.7.0",
    "more-itertools>=8.10.0,<9.0.0",
    "pydantic>=1.8.2,<2.0.0",
    "rich>=10.12.0,<11.0.0",
    "tenacity>=8.0.1,<9.0.0",
    "toml>=0.10.2,<0.11.0",
]

entry_points = {
    "console_scripts": [
        "netcad = netcad.cli.netcad:script",
        "netcam = netcad.cli.netcam:script",
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
