from enum import IntEnum


class PhyPortSpeeds(IntEnum):
    """Physical Port Speeds in value Mbps"""

    speed_100M = 100
    speed_1G = 1_000
    speed_2_5G = 2_500  # 2.5 Gbps
    speed_5G = 5_000
    speed_10G = 10_000
    speed_25G = 25_000
    speed_40G = 40_000
    speed_100G = 100_000
    speed_200G = 200_000
    speed_400G = 400_000

    def __str__(self):
        """return the speed as a string; for rendering purposes"""
        return str(self.value)
