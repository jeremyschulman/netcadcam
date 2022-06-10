# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, TypeVar
from enum import Enum
from dataclasses import dataclass

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["IPNetworkProfile", "IPNetworkEnumIndex"]


P = TypeVar("P")


@dataclass(frozen=True)
class IPNetworkProfile:
    """
    The IPNetworkProfile is a "record" that designates the IP network name,
    address (with prefix), and optionally a link to a parent. The parent is
    used for chaining the "child" record up through the heirarcy of the IP
    address management.

    Notes
    -----
    The dataclass is frozen so that the IPNetworkProfile instance can be used
    as a Hashable.  Useful for dictionary index and sets.
    """

    name: str
    address: str
    parent: Optional["P"] = None


class IPNetworkEnumIndex(IPNetworkProfile, Enum):
    """
    The IPNetworkEnumIndex is used to maintain an enumerated list of symbolic
    identifiers that are assigned to IPNetworkProfile record items.  In this
    manner a Developer can create an "index" of IPNetwork items so that their
    code uses these index enum values rather than string-labels.
    """

    def __init__(self, given: IPNetworkProfile):
        """
        Overload Enum init to allow the Caller to create subclasses that taken
        enumerated assignments of IPNetworkProfile, for example:

            class RootNetworkCatalog(IPNetworkEnumIndex):
                dc1 = IPNetworkProfile(name="Datacenter 1", address="9.12.0.0/17")
                oob_mgmt = IPNetworkProfile(name="All OOB networks", address="192.30.0.0/16")

        Parameters
        ----------
        given: IPNetworkProfile
            The value assigned to the Enum class symbolic attribute during the
            class declaration time; for example the value of "dc1" in the
            example.

        Notes
        -----
        This __init__ is  required because the Enum metaclass would attempt to
        create the enumerated instance ("dc1", for example) by taking the given
        IPNetworkProfile instance and constructing _a new_ intance of
        IPNetworkProfile; this is a behavior of declaring IPNetworkEnumIndex
        with a concrete data-type of IPNetworkProfile.

        References
        ----------
        https://docs.python.org/3/library/enum.html#restricted-enum-subclassing

        """
        # Note: the `noqa` is here because PyCharm thinks that the _value_ is
        # read only since the dataclass is frozen (I am guessing), but the
        # metaclass aspect of Enum allows for this assignment.

        self._value_ = given  # noqa

    @property
    def name(self):
        return self.value.name

    @property
    def address(self):
        return self.value.address

    @property
    def parent(self):
        """
        Return the enumerated parent value.

        Notes
        -----
        The parent attribute could be a callable.  This occurs when a given
        IPNetworkEnumIndex needs to backreference a member as a parent.

        For example:

            class Parent(IPNetworkEnumIndex):
                root = IPNetworkProfile(name='root', address='3.3.3.0/24')

            class Catalog(IPNetworkEnumIndex):
                this = IPNetworkProfile(name='foo', address='1.1.1.0/24')

                # parent in declared Enum
                that = IPNetworkProfile(name='bozo', address='2.2.2.0/24', parent=Parent.root)

                # in same Enum as being declared
                sibling = IPNetworkProfile(name='sib', address='91.92.93.0/24', parent=lambda : Catalog.that)

        In the case of Catalog.sibling, the parent is a backreference to
        another member in the same Catalog. Compare that to the
        Catalog.that.parent is an assignment to Parent.root since that parent
        is in a different Enum.

        Returns
        -------
        The parent, as the enumerated value.
        """
        p = self.value.parent
        return p() if callable(p) else p
