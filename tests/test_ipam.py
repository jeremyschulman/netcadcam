from netcad.ipam import IPNetworkProfile, IPNetworkEnumCatalog


def test_ipam_ip_network():
    ip_net = IPNetworkProfile(name="foo", address="1.1.1.0/24")
    assert ip_net.name == "foo"


def test_ipam_ip_network_catalog():
    class Parent(IPNetworkEnumCatalog):
        root = IPNetworkProfile(name="root", address="3.3.3.0/24")

    class Catalog(IPNetworkEnumCatalog):
        this = IPNetworkProfile(name="foo", address="1.1.1.0/24")
        that = IPNetworkProfile(name="bozo", address="2.2.2.0/24", parent=Parent.root)

        # parent assignment must be lambda since referencing another member in
        # the same enum.  Otherwise, the parent would be referring in the
        # IPNetworkProfile instance and not the enumerated symbolic of the
        # IPNetworkProfile.  ick.  Generally speaking, one should not need to
        # reference a symbolic in the same IPNetworkEnumCatalog, but it could
        # happen.

        sibling = IPNetworkProfile(
            name="sib", address="91.92.93.0/24", parent=lambda: Catalog.that
        )

    assert Catalog.this.address == "1.1.1.0/24"
    assert Catalog.that.parent.address == "3.3.3.0/24"
    assert Catalog.that.parent == Parent.root
    assert Catalog.sibling.parent == Catalog.that
    assert Catalog.sibling.parent.parent == Parent.root
