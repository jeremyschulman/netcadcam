from netcad.registry import Registry
from .test_cases import TestCases

__all__ = ["TestingServices", "testing_service"]


class TestingServices(Registry):
    """
    TestingServices registry used to register TestCases class so that they can
    be looked up by name for the purposes of building tests, ...
    """

    def __call__(self, cls):
        """
        The __call__ method is used a decorator.  For example:

            @testing_services
            class FooTestCases(TestCases):
                service = 'foo-service'
                ...

        The __call__ decorator will validate that the decorating class is of
        type TestCases and has a "services" attribute defined.

        Parameters
        ----------
        cls: type
            The TestCases subclass to register with TestingServices.

        Returns
        -------
        cls - as is
        """

        if not issubclass(cls, TestCases):
            raise RuntimeError(
                f"Forbidden use of TestingService registration on non TestCases class: {cls.__name__}"
            )

        try:
            service_name = cls.get_service_name()
        except (KeyError, AttributeError):
            raise RuntimeError(
                f"TestCases: {cls.__name__}: missing `service` name attribute."
            )

        self.registry_add(service_name, cls)
        return cls


# decorator function is the registration, see __call__ usage above.
testing_service = TestingServices()
