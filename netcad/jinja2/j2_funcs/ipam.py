from netcad.ipam import IPAM


def j2_func_ipam_get(name: str):
    return IPAM.registry_get(name)
