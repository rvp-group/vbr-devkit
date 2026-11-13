"""Resumable, verified HTTP(S) file download."""
import hashlib
import re
import time
from pathlib import Path
from typing import Callable, Optional

import requests

CHUNK_SIZE = 1 << 20  # 1 MiB
DEFAULT_TIMEOUT = (15, 120)  # (connect, read) seconds
USER_AGENT = "vbr-devkit"
_CONTENT_RANGE = re.compile(r"bytes (\d+)-(\d+)/(\d+|\*)")

ProgressCallback = Callable[[int], None]


class DownloadError(Exception):
    """Permanent failure: retrying will not help."""


class _Retryable(Exception):
    """Transient failure: retry, resuming from the bytes already on disk."""


def part_path(dest: Path) -> Path:
    return dest.with_name(dest.name + ".part")


def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(block)
    return h.hexdigest()


def is_complete(dest: Path, size: Optional[int], sha256: Optional[str] = None) -> bool:
    if not dest.is_file():
        return False
    if size is not None and dest.stat().st_size != size:
        return False
    return sha256 is None or sha256sum(dest) == sha256


def fetch(url: str,
          dest: Path,
          size: Optional[int] = None,
          sha256: Optional[str] = None,
          *,
          session: Optional[requests.Session] = None,
          retries: int = 5,
          backoff: float = 2.0,
          timeout=DEFAULT_TIMEOUT,
          on_progress: Optional[ProgressCallback] = None) -> None:
    """Download ``url`` to ``dest``.

    Data is streamed to ``<dest>.part`` and renamed once complete and verified. If a
    ``.part`` file already exists the download resumes from its end with an HTTP
    ``Range`` request; servers that ignore ``Range`` (reply 200) cause a restart.
    Transient errors (connection drops, timeouts, 5xx, 429) are retried up to
    ``retries`` times with exponential backoff, each retry resuming where it stopped.

    ``on_progress`` receives the absolute number of bytes on disk so far.
    Raises :class:`DownloadError` on permanent failure.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = part_path(dest)
    own_session = session is None
    session = session or requests.Session()
    session.headers.setdefault("User-Agent", USER_AGENT)
    try:
        attempt = 0
        while True:
            try:
                _fetch_once(url, part, size, session, timeout, on_progress)
                _verify(part, size, sha256)
                break
            except (_Retryable, requests.RequestException) as exc:
                attempt += 1
                if attempt > retries:
                    raise DownloadError(f"{url}: giving up after {retries} retries ({exc})") from exc
                time.sleep(backoff * (2 ** (attempt - 1)))
        part.replace(dest)
    finally:
        if own_session:
            session.close()


def _fetch_once(url: str,
                part: Path,
                size: Optional[int],
                session: requests.Session,
                timeout,
                on_progress: Optional[ProgressCallback]) -> None:
    offset = part.stat().st_size if part.exists() else 0
    if size is not None and offset > size:  # stale or corrupt partial file
        part.unlink()
        offset = 0
    if size is not None and offset == size:
        return

    headers = {"Range": f"bytes={offset}-"} if offset else {}
    with session.get(url, headers=headers, stream=True, timeout=timeout) as r:
        if r.status_code == 416:  # range starts at/after EOF
            if size is None:
                return
            part.unlink()
            raise _Retryable(f"416 for offset {offset}, restarting")
        if r.status_code == 429 or r.status_code >= 500:
            raise _Retryable(f"HTTP {r.status_code}")
        if r.status_code not in (200, 206):
            raise DownloadError(f"{url}: HTTP {r.status_code}")

        if r.status_code == 206:
            m = _CONTENT_RANGE.match(r.headers.get("Content-Range", ""))
            if not m or int(m.group(1)) != offset:
                part.unlink()
                raise _Retryable("unexpected Content-Range, restarting")
            mode = "ab"
        else:  # 200: server sent the whole file
            offset = 0
            mode = "wb"

        if on_progress:
            on_progress(offset)
        with open(part, mode) as f:
            for block in r.iter_content(CHUNK_SIZE):
                f.write(block)
                offset += len(block)
                if on_progress:
                    on_progress(offset)


def _verify(part: Path, size: Optional[int], sha256: Optional[str]) -> None:
    got = part.stat().st_size if part.exists() else 0
    if size is not None and got != size:
        if got > size:
            part.unlink()
        raise _Retryable(f"size {got} != expected {size}")
    if sha256 is not None and sha256sum(part) != sha256:
        part.unlink()
        raise DownloadError(f"{part.name}: SHA-256 mismatch")
