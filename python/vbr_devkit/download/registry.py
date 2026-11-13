"""Catalogue of downloadable VBR sequences, backed by the bundled ``manifest.json``."""
import json
import os
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional

MANIFEST_PATH = Path(__file__).with_name("manifest.json")
BASE_URL_ENV = "VBR_BASE_URL"


class FileKind(str, Enum):
    calib = "calib"
    gt = "gt"
    bags = "bags"


def file_kind(name: str) -> Optional[FileKind]:
    if name.endswith(".bag"):
        return FileKind.bags
    if name.endswith("_gt.txt"):
        return FileKind.gt
    if name.endswith(".yaml"):
        return FileKind.calib
    return None


@dataclass(frozen=True)
class RemoteFile:
    sequence: str
    location: str
    name: str
    size: int
    sha256: Optional[str]
    url: str

    @property
    def kind(self) -> Optional[FileKind]:
        return file_kind(self.name)

    def local_path(self, output_dir: Path) -> Path:
        """Destination path, mirroring the NAS layout ``vbr_slam/<location>/<sequence>/<name>``."""
        return output_dir / "vbr_slam" / self.location / self.sequence / self.name


def load_manifest(path: Optional[Path] = None) -> dict:
    return _load_manifest(Path(path or MANIFEST_PATH))


@lru_cache(maxsize=None)
def _load_manifest(path: Path) -> dict:
    with open(path) as f:
        manifest = json.load(f)
    if manifest.get("version") != 1:
        raise ValueError(f"Unsupported manifest version: {manifest.get('version')!r}")
    return manifest


def base_url(manifest: Optional[dict] = None) -> str:
    manifest = manifest or load_manifest()
    return os.environ.get(BASE_URL_ENV, manifest["base_url"]).rstrip("/")


def sequences(manifest: Optional[dict] = None) -> List[str]:
    manifest = manifest or load_manifest()
    return sorted(manifest["sequences"])


def resolve_sequences(selector: str, manifest: Optional[dict] = None) -> List[str]:
    """Expand ``all`` / ``train`` / ``test`` / ``<sequence>`` into sequence names."""
    names = sequences(manifest)
    if selector == "all":
        return names
    if selector in ("train", "test"):
        return [n for n in names if f"_{selector}" in n]
    if selector in names:
        return [selector]
    raise KeyError(selector)


def remote_files(seqs: Iterable[str],
                 kinds: Optional[Iterable[FileKind]] = None,
                 manifest: Optional[dict] = None) -> List[RemoteFile]:
    manifest = manifest or load_manifest()
    root = base_url(manifest)
    template = manifest["url_template"]
    wanted = set(kinds) if kinds else None
    out = []
    for seq in seqs:
        entry: Dict = manifest["sequences"][seq]
        for f in entry["files"]:
            if wanted is not None and file_kind(f["name"]) not in wanted:
                continue
            out.append(RemoteFile(
                sequence=seq,
                location=entry["location"],
                name=f["name"],
                size=int(f["size"]),
                sha256=f.get("sha256"),
                url=template.format(base_url=root, sequence=seq, name=f["name"]),
            ))
    return out
