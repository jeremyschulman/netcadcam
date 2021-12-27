# -*- coding: utf-8 -*-
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
    "version": "0.0.1",
    "description": "NetCadCam - Network Automation by Design",
    "long_description": '# NetCadCam - Network Automation by Design\n\nThis repository contains the NetCadCam project core framework library.\n\nThe primary goal of this project is to answer the question:\n> How do we know if a network is operating as designed ?\n\n"Network Automation by Design" is the name I am giving to the concept that\nUser can:\n\n* Declaratively represent the **expected operational state** of a network as\na design\n</br></br>\n* The design can be used to **automatically generate the collection of checks** so\n  that the User can validate the correctness of the actual state of the network\n  against the expected state\n</br></br>\n* The same design can be used to generate the network **device configurations**\n  in order to achieve the expected operational state\n</br></br>\n* The same design can be used to generate **business ready documents** that\n  describe the design in various forms, reports, and diagrams\n\n# The NetCadCam Project\n\nThe NetCadCam is a general purpose python toolkit.  The toolkit is used by a\n"Designer" to declaratively represent the operational state of a network design\nvia a composition of design elements arranged in manner specific to their needs.\nThe toolkit provides two CLI tools `netcad` for the design automation features\nand `netcam` for the features that interactive with the devices, such as\nchecking the operational state.\n\n---\n\n**WARNING**: The netcadcam project is under active development, is very nascent,\nand is not released on PyPi.  Code is subject to change without notice.  Once\nthe API has settled a bit, docs will be written.\n\nThe best way to "see" how this project is used is via the example, found\n[here](https://github.com/jeremyschulman/netcad-demo-clabs1).\n\n---\n\n* **Plugins** - The netcadcam framework takes a "plugin" approach to integration with network\ndevices and external systems, such as Netbox.  At this time there are two device\nintegrations, one for Arista EOS and another for Meraki devices.  These\nintegrations are stored in separate repos.\n</br></br>\n* **Extensible** - Extensible so a User can create new design composition elements to support\nnetwork features specific to their needs; for example Wireless, PTP, multicast,\nequipment vendor specific features, etc.\n</br></br>\n* **Syndication** - Syndicates design artifacts with other systems of record such as Netbox,\nNautobot, InfoBlox, other IPAM products.\n\n## Design Elements\n\nThis core repository contains the following design-elements:\n* Topology\n* VLANs\n* LAGs\n* MLags (Arista)\n* IP Address Management\n\n## Network Device Integrations\nThese device integrations provide the design-element "checking" features.\n\n* [Arista EOS via eAPI](https://github.com/jeremyschulman/netcam-aioeos)\n* Meraki via Dashboard API\n',
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
