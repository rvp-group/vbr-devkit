"""Warn when a newer vbr-devkit release is available on PyPI.

The check runs at most once per day (result cached on disk), uses a short timeout and
never fails the command: any error (offline, PyPI down, unparsable version) is ignored.
Disable it with ``VBR_NO_UPDATE_CHECK=1``.
"""
import json
import os
import re
import time
from pathlib import Path
from typing import Optional, Tuple

import requests

PYPI_URL = "https://pypi.org/pypi/vbr-devkit/json"
DISABLE_ENV = "VBR_NO_UPDATE_CHECK"
CHECK_INTERVAL = 24 * 3600  # seconds
TIMEOUT = 2.0  # seconds


def installed_version() -> str:
    try:
        from importlib.metadata import version
        return version("vbr-devkit")
    except Exception:
        from vbr_devkit import __version__
        return __version__


def parse_version(v: str) -> Optional[Tuple[int, ...]]:
    """Parse a plain release version ("1.2.3"); pre/dev releases return None."""
    if not re.fullmatch(r"\d+(\.\d+)*", v.strip()):
        return None
    return tuple(int(x) for x in v.strip().split("."))


def cache_file() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    return Path(base) / "vbr-devkit" / "update_check.json"


def latest_version(now: Optional[float] = None) -> Optional[str]:
    """Latest version on PyPI, from the daily cache when fresh."""
    now = time.time() if now is None else now
    path = cache_file()
    try:
        cached = json.loads(path.read_text())
        if now - cached["checked_at"] < CHECK_INTERVAL:
            return cached["latest"]
    except Exception:
        pass

    r = requests.get(PYPI_URL, timeout=TIMEOUT)
    r.raise_for_status()
    latest = r.json()["info"]["version"]
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"checked_at": now, "latest": latest}))
    except OSError:
        pass
    return latest


def newer_version_available() -> Optional[str]:
    """Return the newer PyPI version, or None (also on any error or when disabled)."""
    if os.environ.get(DISABLE_ENV):
        return None
    try:
        current = parse_version(installed_version())
        latest = latest_version()
        latest_t = parse_version(latest) if latest else None
        if current and latest_t and latest_t > current:
            return latest
    except Exception:
        pass
    return None


def warn_if_outdated() -> None:
    latest = newer_version_available()
    if latest:
        from rich.console import Console
        Console(stderr=True).print(
            f"[bold yellow]:warning: vbr-devkit {latest} is available (installed: {installed_version()}). "
            f"Update with [bold]pip install -U vbr-devkit[/bold] "
            f"(or [bold]uvx vbr-devkit@latest[/bold]). Set {DISABLE_ENV}=1 to silence this check.", soft_wrap=True)
