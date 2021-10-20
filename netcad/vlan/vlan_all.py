from .vlan_profile import VlanProfile

# declare a sentinal instance to indicate that all VLANs defined on a device
# should be used. this is a common use-case for uplink trunk ports.

SENTIAL_ALL_VLANS = VlanProfile(name="*", vlan_id=1)
VLANS_ALL = [SENTIAL_ALL_VLANS]
