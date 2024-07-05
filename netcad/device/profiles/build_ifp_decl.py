from netcad.logger import get_logger
from netcad.device.profiles import InterfaceProfile, InterfaceProfileRegistry

IFP_BASE_FIELDS = {"desc", "phy_profile", "template", "name"}


def build_interface_profile_from_decl(ifp_decl: dict):
    log = get_logger()
    ifp_name = ifp_decl["name"]
    ifp_attrs = InterfaceProfile.attrs_from_decl(ifp_decl)

    ifp_inhrt_bases = set()

    for base_name, base_attrs in ifp_decl["extends"].items():
        if not (base_cls := InterfaceProfileRegistry.get(base_name)):
            log.error(f"Interface profile base not found: {base_name}")
            continue
        ifp_inhrt_bases.add(base_cls)
        ifp_attrs.update(base_cls.attrs_from_decl(base_attrs))

    def attrs_from_decl(ifp_decl: dict):  # noqa
        return ifp_attrs

    ifp_cls = type(
        ifp_name,
        tuple(ifp_inhrt_bases),
        {
            "attrs_from_decl": attrs_from_decl,
            **ifp_attrs,
        },
    )

    return ifp_cls
