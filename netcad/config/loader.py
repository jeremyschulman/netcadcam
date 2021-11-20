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
