def find_check_services(device, optionals: dict):

    inc_check_names = optionals["testing_service_names"]

    for design_service in device.services.values():
        for check_service in design_service.check_collections:
            check_name = check_service.get_name()

            if inc_check_names:
                if check_name in inc_check_names:
                    yield check_service

                continue

            yield check_service
