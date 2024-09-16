from netcad.logger import get_logger
from netcad.device.profiles import InterfaceProfile, InterfaceProfileRegistry

IFP_BASE_FIELDS = {"desc", "phy_profile", "template", "name"}


def build_interface_profile_from_decl(ifp_decl: dict):
    log = get_logger()
    ifp_name = ifp_decl["name"]
    ifp_attrs = InterfaceProfile.fields_from_decl(ifp_decl)

    ifp_inhrt_bases = set()

    # if the Designer included any "is_" attributes, then add them to the
    # interface profile attribute definition.

    ifp_attrs.update({k: v for k, v in ifp_decl.items() if k.startswith("is_")})

    # handle the "extends" key in the interface profile declaration.  This key
    # is used to handle profile inheritance.

    for base_name, base_attrs in ifp_decl["extends"].items():
        if not (base_cls := InterfaceProfileRegistry.get(base_name)):
            log.error(f"Interface profile base not found: {base_name}")
            continue

        ifp_inhrt_bases.add(base_cls)
        ifp_attrs.update(base_cls.fields_from_decl(base_attrs))

    # declare the new interface profile type.

    ifp_cls = type(
        ifp_name,
        tuple(ifp_inhrt_bases),
        {
            **ifp_attrs,
        },
    )

    # declare the function that allows this profile to be inheretided by other
    # profiles by means of the "attrs from decl" method.

    def fields_from_decl(ifp_decl: dict):  # noqa
        ret = ifp_attrs.copy()

        for cls in (
            b for b in ifp_cls.mro() if b != ifp_cls and issubclass(b, InterfaceProfile)
        ):
            ret.update(cls.fields_from_decl(ifp_decl))

        return ret

    setattr(ifp_cls, "fields_from_decl", staticmethod(fields_from_decl))
    return ifp_cls
