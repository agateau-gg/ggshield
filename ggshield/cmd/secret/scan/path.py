import sys
from typing import List

import click

from ggshield.core.file_utils import get_files_from_paths
from ggshield.core.utils import ScanContext, ScanMode, handle_exception
from ggshield.output import OutputHandler
from ggshield.scan import File, ScanCollection, Files


class ScanProgressBar:
    """
    Creates a click progress bar to monitor a scan. Usage:

    ```
    with ScanProgressBar(files) as progressbar:
    ```
    """
    def __init__(self, files: Files):
        self._bar = click.progressbar(length=len(files.files), label="Scanning", file=sys.stderr)

    def on_file_chunk_scanned(self, chunk: List[File]) -> None:
        self._bar.update(len(chunk))

    def __enter__(self) -> "ScanProgressBar":
        self._bar.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._bar.__exit__(exc_type, exc_val, exc_tb)


@click.command()
@click.argument(
    "paths", nargs=-1, type=click.Path(exists=True, resolve_path=True), required=True
)
@click.option("--recursive", "-r", is_flag=True, help="Scan directory recursively")
@click.option("--yes", "-y", is_flag=True, help="Confirm recursive scan")
@click.pass_context
def path_cmd(
    ctx: click.Context, paths: List[str], recursive: bool, yes: bool
) -> int:  # pragma: no cover
    """
    scan files and directories.
    """
    config = ctx.obj["config"]
    output_handler: OutputHandler = ctx.obj["output_handler"]
    try:
        files = get_files_from_paths(
            paths=paths,
            exclusion_regexes=ctx.obj["exclusion_regexes"],
            recursive=recursive,
            yes=yes,
            verbose=config.verbose,
            # when scanning a path explicitly we should not care if it is a git repository or not
            ignore_git=True,
        )
        scan_context = ScanContext(
            scan_mode=ScanMode.PATH,
            command_path=ctx.command_path,
        )

        with ScanProgressBar(files) as progressbar:
            results = files.scan(
                client=ctx.obj["client"],
                cache=ctx.obj["cache"],
                matches_ignore=config.secret.ignored_matches,
                scan_context=scan_context,
                ignored_detectors=config.secret.ignored_detectors,
                on_file_chunk_scanned=progressbar.on_file_chunk_scanned,
            )
        scan = ScanCollection(id=" ".join(paths), type="path_scan", results=results)

        return output_handler.process_scan(scan)
    except Exception as error:
        return handle_exception(error, config.verbose)
