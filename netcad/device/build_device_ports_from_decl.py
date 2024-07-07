from netcad.device import Device
from netcad.device.profiles.interface_profile import InterfaceProfileRegistry
from netcad.logger import get_logger
from netcad.phy_port import PhyProfileRegistry


def build_device_ports_from_decl(host_port_assignments: dict, dev: Device):
    """
    This function is used to add the device host interface ports to the device
    design.  The port definitions are defined in a TOML file by the name as the
    deviec, for example "dug1b.toml".

    Parameters
    ----------
    host_port_assignments:

    dev:
        The device instance
    """
    log = get_logger()

    # see if there are host port interface assignments for this device. if so,
    # then add those definitions to the device interfaces data obj

    name = dev.alias

    ports = host_port_assignments[name]

    for if_name, assign_def in ports.items():
        profile_name = assign_def.get("profile")
        profile_cls = None

        # ---------------------------------------------------------------------
        # Taking a port out of service via the "Unused" profile
        # ---------------------------------------------------------------------
        # If the profile is set to Unused, then we will use the devices defined
        # "unused port profile" class.  This used profile is generally used
        # with the interface is "not used in the design".  But in this case we
        # want to use the interface in the design to "unuse" the port.
        # Therefore, we need to create an actual instance of the unused-profile
        # class so that the config generator will create the interface stanza
        # to actually shut down the port, and assign the description to
        # "Unused"
        # ---------------------------------------------------------------------

        if profile_name:
            if profile_name == "Unused":
                dev.interfaces[
                    if_name
                ].profile = dev.unused_interface_profile.__class__(
                    desc="UNUSED",
                )
                dev.interfaces[if_name].enabled = False
                continue

            if not (profile_cls := InterfaceProfileRegistry.get(profile_name)):
                log.error(
                    "%s: %s: Unknown interface profile '%s', please check TOML file.",
                    name,
                    if_name,
                    profile_name,
                )
                continue

        # if there is a variant defined for this port need to check the condition
        # TODO: add Variants to core
        # if variants and (has_variant := assign_def.get("variant")):
        #     if not variants.check_variant(name, if_name, has_variant):
        #         continue

        # if the interface name is a mapped name/alias, then convert to the
        # actual interface name

        if if_name_map := dev.interfaces_map.get(if_name):
            if_name = if_name_map

        # create the instance of the switch interface profile and

        with dev.interfaces[if_name] as if_eth:
            # if a profile was defined, then instantiate an instance of that
            # otherwise, use the existing profile.  This could be the case
            # where we just want to change the description, phy_port, or other
            # value.

            if profile_cls:
                if_eth.profile = profile_cls()

            # if the profile is a LAG, then add the lag_members:

            if "lag_members" in assign_def:
                for member in assign_def["lag_members"]:
                    if mbr_map := dev.interfaces_map.get(member):
                        member = mbr_map
                    if_eth.profile.add_lag_members(dev.interfaces[member])

            # -----------------------------------------------------------------
            # set the description field if it is porvided.
            # -----------------------------------------------------------------

            desc = ""
            if host_desc := assign_def.get("host"):
                desc = host_desc

            if host_port := assign_def.get("port"):
                desc += f"-{host_port}"

            if desc:
                if_eth.desc = desc

            # -----------------------------------------------------------------
            # set the enabled field if it is porvided.
            # -----------------------------------------------------------------

            if (enabled_ctrl := assign_def.get("enabled")) is not None:
                if_eth.enabled = enabled_ctrl

            # if the assignment sets the interface speed to a know override
            # value, then override the profile here.

            if phy_ovrd_name := assign_def.get("phy_profile", ""):
                if not (phy_ovrd := PhyProfileRegistry.get(phy_ovrd_name)):
                    log.error(
                        "%s: %s: Unknown speed override '%s', please check TOML file.",
                        name,
                        if_name,
                        phy_ovrd_name,
                    )

                if_eth.profile.phy_profile = phy_ovrd
