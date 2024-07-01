from .vlan_profile import VlanProfile


def build_vlans_from_decl(vlan_decls: dict):
    for vlan_name, vlan_cfg in vlan_decls.items():
        VlanProfile(name=vlan_name, **vlan_cfg)
