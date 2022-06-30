def find_check_services(device, optionals: dict):

    inc_check_names = optionals["testing_service_names"]
    inc_service_names = optionals["service_list"]

    for design_service in device.services.values():
        if inc_check_names:
            if design_service.name not in inc_service_names:
                continue

        for check_service in design_service.check_collections:
            check_name = check_service.get_name()

            if inc_check_names:
                if check_name in inc_check_names:
                    yield check_service

                continue

            yield check_service
