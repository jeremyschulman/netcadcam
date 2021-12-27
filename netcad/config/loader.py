#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import importlib


def import_objectref(object_ref: str):
    """
    This function imports the object specified using the standard Python object reference notation,
    as defined here:
    https://packaging.python.org/specifications/entry-points/

    Parameters
    ----------
    object_ref: str
        The object to import

    Returns
    -------
    The imported object
    """

    modname, qualname_separator, qualname = object_ref.partition(":")
    obj = importlib.import_module(modname)

    if qualname_separator:
        for attr in qualname.split("."):
            obj = getattr(obj, attr)

    return obj
