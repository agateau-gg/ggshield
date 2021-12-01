from abc import ABC, abstractmethod
from typing import Optional, Tuple

import click

from ggshield.scan import ScanCollection


class OutputHandler(ABC):
    show_secrets: bool = False
    verbose: bool = False
    output: Optional[str] = None

    def __init__(
        self,
        show_secrets: bool,
        verbose: bool,
        output: Optional[str] = None,
    ):
        self.show_secrets = show_secrets
        self.verbose = verbose
        self.output = output

    def process_scan(self, scan: ScanCollection) -> int:
        """Process a scan collection, write the report to :attr:`self.output`

        :param scan: The scan collection to process
        :return: The exit code
        """
        text, exit_code = self._process_scan_impl(scan)
        if self.output:
            with open(self.output, "w+") as f:
                f.write(text)
        else:
            click.echo(text)
        return exit_code

    @abstractmethod
    def _process_scan_impl(self, scan: ScanCollection) -> Tuple[str, int]:
        """Implementation of scan processing,
        called by :meth:`OutputHandler.process_scan`

        :param scan: The scan collection to process
        :return: A tuple of content, exit code
        """
        return "", -1
