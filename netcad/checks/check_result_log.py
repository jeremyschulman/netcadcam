from typing import List, Optional
from functools import partial

from rich.table import Table, Text
from rich.pretty import Pretty
from pydantic import Field, RootModel

from netcad.checks.check_status import CheckStatus


class CheckResultLogs(RootModel):
    """
    The CheckResultLog is a field within the CheckResult class.  It is used to
    store the check-result logging information so that it can be expressed to
    the User in an easy manner.
    """

    root: List = Field(default_factory=list)

    def pretty_table(self, table: Optional[Table] = None) -> Table:
        if not table:
            table = Table(show_header=False, box=None)

        status_id_hash = {id(log): CheckStatus(log[0]) for log in self.__root__}

        def sorted_by_status(_log):
            return status_id_hash[id(_log)].to_flag()

        for log in sorted(self.__root__, key=sorted_by_status, reverse=True):
            st_enum = status_id_hash[id(log)]
            status, field, log_info = log

            if st_enum == CheckStatus.PASS:
                log_info = log_info["expected"]

            table.add_row(
                Text(status, style=st_enum.to_style()), field, Pretty(log_info)
            )

        return table

    def log(self, /, status, field, data):
        self.__root__.append([status, field, data])

    def __getattr__(self, item):
        """
        Define the getattr oberload so the caller can invite the logging methods
        that map to the various status levels.

        Parameters
        ----------
        item: str
            The name of the logging level, for example "pass" or "fail"
        """
        try:
            as_status = CheckStatus(item)
            return partial(self.log, as_status)
        except ValueError:
            return None
