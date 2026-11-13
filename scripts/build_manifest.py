#!/usr/bin/env python3
"""Build ``vbr_devkit/download/manifest.json`` from a listing of the NAS data tree.

The listing is a TSV with one ``<location>/<sequence>/<file>\\t<size>`` row per file,
produced on the NAS with::

    cd /volume2/srrg_datasets/vbr_slam
    find . -mindepth 3 -maxdepth 3 -type f -printf '%P\\t%s\\n' | sort > vbr_files.tsv

Optionally pass ``--sha256 SUMS`` with ``sha256sum``-style lines
(``<hash>  <location>/<sequence>/<file>``) to embed checksums.

Usage::

    python scripts/build_manifest.py vbr_files.tsv [--sha256 SHA256SUMS] \\
        [-o python/vbr_devkit/download/manifest.json]
"""
import argparse
import json
import re
from pathlib import Path

SEQ_RE = re.compile(r"^[a-z]+_(train|test)\d+$")
KEEP_SUFFIXES = (".bag", ".yaml", ".txt")
DEFAULT_OUT = Path(__file__).resolve().parents[1] / "python" / "vbr_devkit" / "download" / "manifest.json"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("listing", type=Path, help="TSV listing: <loc>/<seq>/<file>\\t<size>")
    ap.add_argument("--sha256", type=Path, help="sha256sum output for the same tree")
    ap.add_argument("--base-url", default="https://www.diag.uniroma1.it")
    ap.add_argument("-o", "--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    hashes = {}
    if args.sha256:
        for line in args.sha256.read_text().splitlines():
            if line.strip():
                digest, path = line.split(maxsplit=1)
                hashes[path.lstrip("*").lstrip("./")] = digest

    sequences = {}
    for line in args.listing.read_text().splitlines():
        if not line.strip():
            continue
        rel, size = line.rsplit("\t", 1)
        location, seq, name = rel.lstrip("./").split("/")
        if not SEQ_RE.match(seq) or not name.endswith(KEEP_SUFFIXES):
            continue
        entry = sequences.setdefault(seq, {"location": location, "files": []})
        entry["files"].append({"name": name, "size": int(size), "sha256": hashes.get(rel.lstrip("./"))})

    for entry in sequences.values():
        entry["files"].sort(key=lambda f: f["name"])

    manifest = {
        "version": 1,
        "base_url": args.base_url,
        "url_template": "{base_url}/{sequence}/{name}",
        "sequences": dict(sorted(sequences.items())),
    }
    args.output.write_text(json.dumps(manifest, indent=1) + "\n")
    n_files = sum(len(s["files"]) for s in sequences.values())
    print(f"wrote {args.output}: {len(sequences)} sequences, {n_files} files")


if __name__ == "__main__":
    main()
