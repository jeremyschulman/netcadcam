# -*- coding: utf-8 -*-
from setuptools import setup

packages = [
    "netcad",
    "netcad.arango",
    "netcad.cabling",
    "netcad.cli",
    "netcad.cli.cli_audit",
    "netcad.cli.cli_build",
    "netcad.cli.cli_design",
    "netcad.cli.cli_get",
    "netcad.config",
    "netcad.design_service",
    "netcad.device",
    "netcad.init",
    "netcad.jinja2",
    "netcad.jinja2.filters",
    "netcad.jinja2.funcs",
    "netcad.netbox",
    "netcad.origin",
    "netcad.testing",
    "netcad.testing.cabling",
    "netcad.testing.device",
    "netcad.testing.interfaces",
    "netcad.testing.lags",
    "netcad.testing.mlags",
    "netcad.testing.transceivers",
    "netcad.testing.vlans",
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

entry_points = {"console_scripts": ["netcad = netcad.cli:script"]}

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
