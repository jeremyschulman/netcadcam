# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from netcad.cli.clig_netcad_show import clig_design_show

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


@clig_design_show.group(name="bgp")
def clig_show_bgp():
    """show BGP design commands"""
    pass
