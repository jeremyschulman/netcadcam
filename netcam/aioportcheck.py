# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional
import socket
import asyncio

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------


from httpx import URL

# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = ["port_check_url"]

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


async def port_check_host(host: str, port: int, timeout: Optional[int] = 5) -> bool:
    """
    General purpose "check to see if a port is open on a host" function. Return
    True if it is, False if it is not within the given timeout (second).

    Parameters
    ----------
    host: str
        The host or IP address of the target system

    port: int
        The port number to check

    timeout: int
        The timeout in seconds to wait before declaring False.
    """
    try:
        wr: asyncio.StreamWriter
        _, wr = await asyncio.wait_for(
            asyncio.open_connection(host=host, port=port), timeout=timeout
        )

        # MUST close if opened!
        wr.close()
        return True

    except Exception:  # noqa
        return False


async def port_check_url(url: URL, timeout: Optional[int] = 5) -> bool:
    """
    This function attempts to open the port designated by the URL given the
    timeout in seconds.  If the port is avaialble then return True; False
    otherwise.

    Parameters
    ----------
    url:
        The URL that provides the target system

    timeout: optional, default is 5 seonds
        Time to await for the port to open in seconds
    """
    return await port_check_host(
        host=url.host,
        port=url.port or socket.getservbyname(url.scheme),
        timeout=timeout,
    )
