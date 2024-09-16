#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# -----------------------------------------------------------------------------
# Systeme Imports
# -----------------------------------------------------------------------------

from typing import Optional, TypeVar

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from netcad.design.design_feature import DesignFeature

# -----------------------------------------------------------------------------
# Private Module Imports
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["VarpDesignService", "VarpDesignServiceLike"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


class VarpDesignService(DesignFeature, registry_name="varp"):
    """
    The VARP Design Service is specific to Arista EOS.
    """

    DEFAULT_SERVICE_NAME = "varp"

    CHECK_COLLECTIONS = []

    def __init__(self, feature_name: Optional[str] = None, **kwargs):
        super(VarpDesignService, self).__init__(
            feature_name=feature_name or self.DEFAULT_SERVICE_NAME, **kwargs
        )

    def validate(self):
        pass

    def build(self):
        pass


VarpDesignServiceLike = TypeVar(
    "VarpDesignServiceLike", VarpDesignService, DesignFeature
)
