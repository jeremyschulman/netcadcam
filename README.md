# NetCadCam - Network Automation by Design

This repository contains the NetCadCam project core framework library.

The primary goal of this project is to answer the question:
> How do we know if a network is operating as designed ?

"Network Automation by Design" is the name I am giving to the concept that
User can:

* Declaratively represent the **expected operational state** of a network as
a design
</br></br>
* The design can be used to **automatically generate the collection of checks** so
  that the User can validate the correctness of the actual state of the network
  against the expected state
</br></br>
* The same design can be used to generate the network **device configurations**
  in order to achieve the expected operational state
</br></br>
* The same design can be used to generate **business ready documents** that
  describe the design in various forms, reports, and diagrams

# The NetCadCam Project

The NetCadCam is a general purpose python toolkit.  The toolkit is used by a
"Designer" to declaratively represent the operational state of a network design
via a composition of design elements arranged in manner specific to their needs.
The toolkit provides two CLI tools `netcad` for the design automation features
and `netcam` for the features that interactive with the devices, such as
checking the operational state.

---

**WARNING**: The netcadcam project is under active development, is very nascent,
and is not released on PyPi.  Code is subject to change without notice.  Once
the API has settled a bit, docs will be written.

The best way to "see" how this project is used is via the example, found
[here](https://github.com/jeremyschulman/netcad-demo-clabs1).

---

* **Plugins** - The netcadcam framework takes a "plugin" approach to integration with network
devices and external systems, such as Netbox.  At this time there are two device
integrations, one for Arista EOS and another for Meraki devices.  These
integrations are stored in separate repos.
</br></br>
* **Extensible** - Extensible so a User can create new design composition elements to support
network features specific to their needs; for example Wireless, PTP, multicast,
equipment vendor specific features, etc.
</br></br>
* **Syndication** - Syndicates design artifacts with other systems of record such as Netbox,
Nautobot, InfoBlox, other IPAM products.

## Design Elements

This core repository contains the following design-elements:
* Topology
* VLANs
* LAGs
* MLags (Arista)
* IP Address Management

## Network Device Integrations
These device integrations provide the design-element "checking" features.

* [Arista EOS via eAPI](https://github.com/jeremyschulman/netcam-aioeos)
* Meraki via Dashboard API
