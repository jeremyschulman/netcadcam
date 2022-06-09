from typing import Optional, TypeVar
from enum import Enum
from dataclasses import dataclass

P = TypeVar("P")


@dataclass(frozen=True)
class IPNetworkProfile:
    """
    The IPNetworkItem is a "record" that designates the IP network name,
    address (with prefix), and optionally a link to a parent IPNetworkItem.
    The parent is used for chaining the "child" record up through the heirarcy
    of the IP address management.
    """

    name: str
    address: str
    parent: Optional["P"] = None


class IPNetworkEnumCatalog(IPNetworkProfile, Enum):
    """
    The IPNetworkCatalog is used to maintain an enumerated list of symbolic
    identifiers that are assigned to IPNetwork record items.  In this manner a
    Developer can create a "catalog" of IPNetwork items so that their code uses
    these index enum values rather than string-labels.
    """

    def __init__(self, given):
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

        The parent attribute could be a callable.  This occurs when a given
        IPNetworkEnumCatalog needs to backreference a member as a parent.

        For example:

            class Parent(IPNetworkEnumCatalog):
                root = IPNetworkProfile(name='root', address='3.3.3.0/24')

            class Catalog(IPNetworkEnumCatalog):
                this = IPNetworkProfile(name='foo', address='1.1.1.0/24')
                that = IPNetworkProfile(name='bozo', address='2.2.2.0/24', parent=Parent.root)
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
