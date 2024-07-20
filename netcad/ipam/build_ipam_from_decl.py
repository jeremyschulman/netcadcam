from typing import Literal, Optional
from pydantic import BaseModel, Field, IPvAnyNetwork, RootModel
from ipaddress import ip_network

from netcad.ipam import IPAM


class IPNetworkMapHosts(RootModel):
    root: dict[str, int] = Field(description="Host mapping to IP address host octet")


class IPNetworkMapHostsSubnet(BaseModel):
    hosts: dict[str, int] = Field(description="Host mapping to IP address host octet")


class IPNetworkMapDec(BaseModel):
    name: str = Field(description="Name of network, should match IPAM system")
    network: IPvAnyNetwork = Field(description="Network address")
    mode: Literal["abs", "offset"] = Field(
        # 'abs' is absolute, 'offset' is additive to network base address
        "abs",
        description="IP address assignment mode",
    )
    host_prefixlen: int = Field(
        None,
        description="Host prefix length overrides network prefix length",
        gt=0,
        le=128,
    )
    hosts: Optional[IPNetworkMapHosts] = None
    subnet: Optional[dict[str, IPNetworkMapHostsSubnet]] = None


def build_ipam_from_decl(ipam_decl, ipam: IPAM):
    ip_nmap = IPNetworkMapDec(**ipam_decl)

    ip_net = ipam.network(ip_nmap.name, ip_network(ip_nmap.network))

    def add_hosts(_hosts, _addn_offset=0):
        for key, host_oct in _hosts.items():
            if ip_nmap.mode == "abs":
                host_oct = (
                    host_oct
                    - ip_net.ip_network.network_address.packed[-1]
                    + _addn_offset
                )

            ip_net.interface(
                key, host_offset=host_oct, new_prefix=ip_nmap.host_prefixlen
            )

    if isinstance(ip_nmap.hosts, IPNetworkMapHosts):
        add_hosts(ip_nmap.hosts.root)
        return

    for subnet, hosts in ip_nmap.subnet.items():
        ip_subnet = ip_network(subnet)
        addn_offset = int(ip_subnet.network_address) - int(
            ip_net.ip_network.network_address
        )
        add_hosts(hosts.hosts, addn_offset)
