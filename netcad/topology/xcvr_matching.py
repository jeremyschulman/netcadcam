#  Copyright (c) 2022 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Tuple
from functools import lru_cache

from netcad.config import netcad_globals

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "get_transciver_model_alias",
    "get_transciver_type_alias",
    "transceiver_model_matches",
    "transceiver_type_matches",
]


@lru_cache()
def get_transciver_model_alias(model: str) -> str | None:
    """
    Function used to take a given transceiver model value and perform a lookup
    into the User `netcad.toml` configuration under [transceivers.models] so
    that specific models can be mapped into the Designer expect model values.

    Parameters
    ----------
    model: str
        The transceiver model as retrieved from the device.

    Returns
    -------
    The mapped model name, if the model value exists in their `netcad.toml`
    configuration file; None otherwise.
    """
    config = netcad_globals.g_config.get("transceivers", {}).get("models")
    return None if not config else config.get(model)


@lru_cache()
def transceiver_model_matches(given_mdoel, expected_model) -> bool:
    return (
        given_mdoel == expected_model
        or get_transciver_model_alias(given_mdoel) == expected_model
    )


@lru_cache()
def get_transciver_type_alias(xcvr_type: str) -> str | None:
    """
    Function used to take a given transceiver type value and perform a lookup
    into the User `netcad.toml` configuration under [transceivers.models] so
    that specific models can be mapped into the Designer expect model values.

    Parameters
    ----------
    xcvr_type: str
        The transceiver type as retrieved from the device.

    Returns
    -------
    The mapped model name, if the model value exists in their `netcad.toml`
    configuration file; None otherwise.
    """
    config = netcad_globals.g_config.get("transceivers", {}).get("types")
    return None if not config else config.get(xcvr_type)


@lru_cache()
def transceiver_type_matches(given_type: str, expected_type: str) -> bool:
    return (
        given_type == expected_type
        or get_transciver_type_alias(given_type) == expected_type
    )


@lru_cache()
def transciever_matches(
    given_model_type: Tuple[str, str], expected_model_type: Tuple[str, str]
) -> bool:
    return transceiver_model_matches(
        given_model_type[0], expected_model_type[0]
    ) and transceiver_type_matches(given_model_type[1], expected_model_type[1])
