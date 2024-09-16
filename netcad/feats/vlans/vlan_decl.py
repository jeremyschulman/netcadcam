from .vlan_profile import VlanProfile


def build_vlans_from_decl(vlan_decls: dict):
    for vlan_cfg in vlan_decls:
        VlanProfile(**vlan_cfg)
