from .loader import netcad_import_package


def init_import_device_types(config: dict):
    """
    This function is used to the import any of the 'device-type' packages
    defined in the User configuration files.

    Parameters
    ----------
    config: dict
        The User NETCAD config file contents
    """

    if not (user_device_type_configs := config.get("device-types")):
        return

    for dt_cfg in user_device_type_configs:
        if not (pkg_mod := dt_cfg.get("package")):
            # TODO: should be a log warning or error
            continue

        netcad_import_package(pkg_name=pkg_mod)
