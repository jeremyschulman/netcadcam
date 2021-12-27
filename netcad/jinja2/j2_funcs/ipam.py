#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from netcad.ipam import IPAM


def j2_func_ipam_get(name: str):
    return IPAM.registry_get(name)
