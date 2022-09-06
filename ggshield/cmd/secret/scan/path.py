import sys
from typing import Iterable, List, Optional, Set

import click
from pygitguardian import GGClient

from ggshield.core.cache import Cache
from ggshield.core.file_utils import get_files_from_paths
from ggshield.core.types import IgnoredMatch
from ggshield.core.utils import ScanContext, ScanMode, handle_exception
from ggshield.output import OutputHandler
from ggshield.scan import File, Files, Results, ScanCollection


class ScanUI:
    def scan(
        self,
        files: Files,
        client: GGClient,
        cache: Cache,
        matches_ignore: Iterable[IgnoredMatch],
        scan_context: ScanContext,
        ignored_detectors: Optional[Set[str]] = None,
    ) -> Results:
        raise NotImplementedError


class ProgressBarScanUI(ScanUI):
    def scan(
        self,
        files: Files,
        client: GGClient,
        cache: Cache,
        matches_ignore: Iterable[IgnoredMatch],
        scan_context: ScanContext,
        ignored_detectors: Optional[Set[str]] = None,
    ) -> Results:
        with click.progressbar(
            length=len(files.files), label="Scanning", file=sys.stderr
        ) as progressbar:

            def on_file_chunk_scanned(chunk: List[File]) -> None:
                progressbar.update(len(chunk))

            return files.scan(
                client,
                cache,
                matches_ignore,
                scan_context,
                ignored_detectors,
                on_file_chunk_scanned=on_file_chunk_scanned,
            )


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

        scan_ui = ProgressBarScanUI()
        results = scan_ui.scan(
            files,
            client=ctx.obj["client"],
            cache=ctx.obj["cache"],
            matches_ignore=config.secret.ignored_matches,
            scan_context=scan_context,
            ignored_detectors=config.secret.ignored_detectors,
        )
        scan = ScanCollection(id=" ".join(paths), type="path_scan", results=results)

        return output_handler.process_scan(scan)
    except Exception as error:
        return handle_exception(error, config.verbose)
