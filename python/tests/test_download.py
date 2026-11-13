import json
import os

import pytest

from vbr_devkit.download import registry
from vbr_devkit.download.download_data import download_sequences
from vbr_devkit.download.registry import FileKind, load_manifest, remote_files, resolve_sequences

EXPECTED = {f"{loc}_{split}{i}" for loc in ("pincio", "colosseo", "diag", "spagna")
            for split in ("train", "test") for i in (0,)}
EXPECTED |= {f"{loc}_{split}{i}" for loc in ("campus", "ciampino")
             for split in ("train", "test") for i in (0, 1)}


def test_bundled_manifest_is_complete():
    m = load_manifest()
    assert set(m["sequences"]) == EXPECTED
    for name, seq in m["sequences"].items():
        names = [f["name"] for f in seq["files"]]
        assert "vbr_calib.yaml" in names
        assert any(n.endswith(".bag") for n in names)
        assert (f"{name}_gt.txt" in names) == ("_train" in name)
        assert name.startswith(seq["location"] + "_")
        assert all(f["size"] > 0 for f in seq["files"])


def test_resolve_sequences():
    assert len(resolve_sequences("all")) == 16
    assert all("_train" in s for s in resolve_sequences("train"))
    assert all("_test" in s for s in resolve_sequences("test"))
    assert resolve_sequences("pincio_train0") == ["pincio_train0"]
    with pytest.raises(KeyError):
        resolve_sequences("nope")


def test_urls_and_kinds(monkeypatch):
    monkeypatch.setenv(registry.BASE_URL_ENV, "https://mirror.example/")
    files = remote_files(["pincio_train0"], [FileKind.calib, FileKind.gt])
    assert {f.name for f in files} == {"vbr_calib.yaml", "pincio_train0_gt.txt"}
    assert files[0].url.startswith("https://mirror.example/pincio_train0/")


@pytest.fixture
def fake_dataset(server, tmp_path, monkeypatch):
    """Two tiny sequences served by the fake server, with a matching manifest."""
    content = {
        "foo_train0": {"vbr_calib.yaml": b"calib", "foo_train0_gt.txt": b"gt" * 10,
                       "foo_train0_00.bag": os.urandom(5000)},
        "foo_test0": {"vbr_calib.yaml": b"calib", "foo_test0_00.bag": os.urandom(3000)},
    }
    manifest = {"version": 1, "base_url": "http://unused", "url_template": "{base_url}/{sequence}/{name}",
                "sequences": {}}
    for seq, files in content.items():
        manifest["sequences"][seq] = {"location": "foo", "files": [
            {"name": n, "size": len(d), "sha256": None} for n, d in files.items()]}
        for n, d in files.items():
            server.files[f"/{seq}/{n}"] = d
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    monkeypatch.setattr(registry, "MANIFEST_PATH", path)
    monkeypatch.setenv(registry.BASE_URL_ENV, server.url)
    return content


def test_download_layout_and_skip(server, fake_dataset, tmp_path):
    out = tmp_path / "data"
    assert download_sequences(["foo_train0", "foo_test0"], out, backoff=0) == []
    for seq, files in fake_dataset.items():
        for n, d in files.items():
            assert (out / "vbr_slam" / "foo" / seq / n).read_bytes() == d

    n_requests = len(server.requests)
    assert download_sequences(["foo_train0", "foo_test0"], out, backoff=0) == []
    assert len(server.requests) == n_requests  # everything skipped


def test_only_and_dry_run(server, fake_dataset, tmp_path):
    out = tmp_path / "data"
    download_sequences(["foo_train0"], out, kinds=[FileKind.gt], dry_run=True)
    assert server.requests == []
    download_sequences(["foo_train0"], out, kinds=[FileKind.gt], backoff=0)
    assert [p for p, _ in server.requests] == ["/foo_train0/foo_train0_gt.txt"]


def test_failure_continues(server, fake_dataset, tmp_path):
    del server.files["/foo_test0/vbr_calib.yaml"]
    out = tmp_path / "data"
    failed = download_sequences(["foo_test0"], out, backoff=0)
    assert [f.name for f in failed] == ["vbr_calib.yaml"]
    assert (out / "vbr_slam" / "foo" / "foo_test0" / "foo_test0_00.bag").exists()
