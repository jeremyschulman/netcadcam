from typing import Optional, Any, Set, Dict, AnyStr


class Registry(object):
    """
    Registry mechanism that allows instances of the given class, generally
    called by the class __init__ method.  See the Device class for example.
    """

    __registry = None

    def __init_subclass__(cls, **kwargs):
        """each subclass will be given a unique registry dictionary"""
        cls.__registry = dict()

    @classmethod
    def registry_add(cls, name, obj):
        """add the named object to the registry"""
        cls.__registry[name] = obj

    @classmethod
    def registry_get(cls, name: str) -> Optional[Any]:
        """
        Return the registered item designative by 'name', or None if not found.
        This search will start with the class used in by the Caller, and if not
        found there, will check any subclassed registries.

        Parameters
        ----------
        name: str
            The registered name.

        Returns
        -------
        The object that was registered by the given name if found.
        None if not found.
        """
        return next(
            (
                # return the object given by name
                each_cls.__registry.get(name)
                # check _this_ class, and then any subclasses.
                for each_cls in (cls, *cls.__subclasses__())
                # if the name is in the registry then return this object
                if name in each_cls.__registry
            ),
            # Nothing found, so return None to Caller
            None,
        )

    @classmethod
    def registry_list(cls, subclasses=False) -> Set[str]:
        """
        Return a list of the named objects in the registry.  By default all
        items including subclasses of the registry are returned.  If the Caller
        wants only _this class_ registry, then set subclass=False.

        Parameters
        ----------
        subclasses: bool
            Determines whether or not to include subclassed registries.

        Returns
        -------
        List of the registered names.
        """
        if not subclasses:
            return set(cls.__registry)

        return {
            name
            for each_cls in (cls, *cls.__subclasses__())
            for name in each_cls.__registry.keys()
        }

    @classmethod
    def registry_items(cls, subclasses=False) -> Dict[AnyStr, Any]:
        """
        Return a list of the named objects in the registry.  By default all
        items including subclasses of the registry are returned.  If the Caller
        wants only _this class_ registry, then set subclass=False.

        Parameters
        ----------
        subclasses: bool
            Determines whether or not to include subclassed registries.

        Returns
        -------
        List of the registered names.
        """
        if not subclasses:
            return set(cls.__registry)

        items = {
            item
            for each_cls in (cls, *cls.__subclasses__())
            for item in each_cls.__registry.items()
        }

        return dict(items)
