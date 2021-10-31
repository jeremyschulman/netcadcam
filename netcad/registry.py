# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Any, Set, Dict

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["Registry"]


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class _RegistryFactory(object):
    """
    Registry mechanism that allows instances of the given class, generally
    called by the class __init__ method.  See the Device class for example.
    """

    _registry = None
    _registry_is_private = False

    def __init_subclass__(cls, **kwargs):
        if not getattr(cls, "_registry", None):
            cls._registry = dict()

    @classmethod
    def registry_is_private(cls):
        return cls._registry_is_private

    @classmethod
    def registry_subclasses(cls):
        for subclass in cls.__subclasses__():
            yield from subclass.registry_subclasses()
            yield subclass

    @classmethod
    def registry_add(cls, name, obj):
        """add the named object to the registry"""
        cls._registry[name] = obj

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
                each_cls._registry.get(name)
                # check _this_ class, and then any subclasses.
                for each_cls in (cls, *cls.registry_subclasses())
                # if the name is in the registry then return this object
                if name in each_cls._registry
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
            return set(cls._registry)

        return {
            name
            for each_cls in (cls, *cls.registry_subclasses())
            for name in each_cls._registry.keys()
        }

    @classmethod
    def registry_items(cls, subclasses=False) -> Dict:
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
        Dictionary of registered items.
        """
        if not subclasses:
            return cls._registry

        items = {
            item
            for each_cls in (cls, *cls.registry_subclasses())
            for item in each_cls._registry.items()
        }

        return dict(items)


class Registry(_RegistryFactory):
    def __init_subclass__(cls, registry_name: Optional[str] = None, **kwargs):
        # print(f"new class is {cls.__name__}")`
        # print(f"Registry is {id(Registry._registry)}")
        orig_r = cls._registry
        # print(f"orig_r is {id(orig_r)}")
        new_r = dict()
        # print(f"new_r is {id(new_r)}")

        if registry_name:
            orig_r[registry_name] = cls

        setattr(cls, "_registry", new_r)
        # print(f"Registry after is {id(Registry._registry)}")
