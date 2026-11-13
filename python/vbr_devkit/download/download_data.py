"""Download VBR sequences over HTTPS."""
from pathlib import Path
from typing import Iterable, List, Optional

import requests
from rich.panel import Panel
from rich.progress import (BarColumn, DownloadColumn, Progress, TextColumn, TimeRemainingColumn,
                           TransferSpeedColumn)
from rich.table import Table

from vbr_devkit.download.registry import FileKind, RemoteFile, remote_files, sequences
from vbr_devkit.download.transfer import DownloadError, fetch, is_complete
from vbr_devkit.tools.console import console

vbr_downloads = sequences()


def human_readable_size(size: float, decimal_places: int = 2) -> str:
    for unit in ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]:
        if size < 1024.0 or unit == "PiB":
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


def _plan_table(files: List[RemoteFile], skip: set) -> Table:
    table = Table(box=None, show_header=True, header_style="bold")
    table.add_column("File")
    table.add_column("Size", justify="right")
    table.add_column("Status")
    for f in files:
        status = "[green]present" if f in skip else ""
        table.add_row(f"{f.sequence}/{f.name}", human_readable_size(f.size), status)
    return table


def download_sequences(seqs: Iterable[str],
                       output_dir: Path,
                       kinds: Optional[Iterable[FileKind]] = None,
                       skip_existing: bool = True,
                       verify: bool = True,
                       dry_run: bool = False,
                       retries: int = 5,
                       backoff: float = 2.0) -> List[RemoteFile]:
    """Download the given sequences into ``output_dir/vbr_slam/<location>/<sequence>/``.

    Returns the list of files that failed (empty on success).
    """
    files = remote_files(seqs, kinds)
    skip = set()
    if skip_existing:
        # Full-file hashing of existing multi-GB bags is slow: only size is checked here,
        # freshly downloaded files are hashed when a checksum is available.
        skip = {f for f in files if is_complete(f.local_path(output_dir), f.size)}
    todo = [f for f in files if f not in skip]

    total = sum(f.size for f in files)
    remaining = sum(f.size for f in todo)
    console.print(Panel(_plan_table(files, skip),
                        title=f"{len(files)} files, {human_readable_size(total)} "
                              f"({human_readable_size(remaining)} to download)"))
    if dry_run or not todo:
        if not todo:
            console.print(":white_check_mark: Everything already downloaded")
        return []

    failed: List[RemoteFile] = []
    with requests.Session() as session, Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(binary_units=True),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console) as progress:
        overall = progress.add_task("[bold]Total", total=remaining)
        done_before = 0
        for f in todo:
            task = progress.add_task(f"{f.sequence}/{f.name}", total=f.size)

            def on_progress(n: int, task=task, base=done_before) -> None:
                progress.update(task, completed=n)
                progress.update(overall, completed=base + n)

            try:
                fetch(f.url, f.local_path(output_dir), f.size, f.sha256 if verify else None,
                      session=session, retries=retries, backoff=backoff, on_progress=on_progress)
            except DownloadError as exc:
                progress.console.log(f"[bold red]:x: {f.sequence}/{f.name}: {exc}")
                failed.append(f)
            done_before += f.size
            progress.update(overall, completed=done_before)
            progress.remove_task(task)

    if failed:
        console.print(f"[bold red]{len(failed)} file(s) failed. Re-run the same command to resume.")
    else:
        console.print(":tada: Completed")
    return failed
