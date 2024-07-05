import re
from netcad.logger import get_logger
from netcad.design import Design


def build_cabling_from_decl(cabling_tables: list[dict], design: Design):
    dev_alias_map = {dev.alias: dev for dev in design.devices.values()}
    log = get_logger()

    for table in cabling_tables:
        for row in table["cables"]:
            dev_alias_1, if_alias_1, dev_alias_2, if_alias_2 = re.split(r",\s*", row)

            dev_1 = dev_alias_map.get(dev_alias_1)
            if_1 = dev_1.interfaces.get(dev_1.interfaces_map.get(if_alias_1))

            dev_2 = dev_alias_map.get(dev_alias_2)
            if_2 = dev_2.interfaces.get(dev_2.interfaces_map.get(if_alias_2))

            if not all((dev_1, dev_2, if_1, if_2)):
                log.error(
                    "Cabling table references unknown device or interface, %s", row
                )
                continue

            if_1.cable_peer, if_2.cable_peer = if_2, if_1
