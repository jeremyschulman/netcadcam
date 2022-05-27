#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Any, Set, Dict, Tuple

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
    def registry_get(
        cls, name: str, with_registry=False
    ) -> Any | Tuple[Any, Any] | None:
        """
        Return the registered item designative by 'name', or None if not found.
        This search will start with the class used in by the Caller, and if not
        found there, will check any subclassed registries.

        When the item is found and  `with_registry` is True then the retun will be
        a tuple (item, Registry instance)

        Parameters
        ----------
        name: str
            The registered name.

        with_registry: bool
            When True the return value will be Tuple that includes the specific
            registry class that "ownes" the item. When False (default) only
            the item is returned.
        """
        owner, item = next(
            (
                # return the object given by name
                (each_cls, each_cls._registry.get(name))
                # check _this_ class, and then any subclasses.
                for each_cls in (cls, *cls.registry_subclasses())
                # if the name is in the registry then return this object
                if name in each_cls._registry
            ),
            # Nothing found, so return None to Caller
            (None, None),
        )

        return item if not with_registry else (item, owner)

    @classmethod
    def registry_remove(cls, name: str) -> Optional[Any]:
        item, reg_cls = cls.registry_get(name, with_registry=True)
        if not item:
            # TODO: probably should raise an exception if not found?
            #       for now, return None
            return None

        del reg_cls._registry[item.name]  # noqa
        return item

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
        """
        This method is called when a new subclass of Registry, or its
        decendants, is declared in code.

        Parameters
        ----------
        registry_name
        kwargs

        Returns
        -------

        """
        # if the subclass definition cantqains the keyword `registry_name` then
        # register this new class with the parent class.  At this point the
        # _registry will be in the parent getattr resolution.

        if registry_name:
            cls._registry[registry_name] = cls

        cls._registry = dict()
