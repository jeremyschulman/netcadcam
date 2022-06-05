from ipaddress import IPv4Interface


class VirtualIPv4Interface(IPv4Interface):
    def __init__(self, interface: IPv4Interface, hostoct: int):
        pflen = int(interface.netmask).bit_count()
        base_ip = interface.ip + hostoct
        super().__init__((base_ip, pflen))

        self.primary_ip = IPv4Interface((base_ip + 1, pflen))
        self.secondary_ip = IPv4Interface((base_ip + 2, pflen))
