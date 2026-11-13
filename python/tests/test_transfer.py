import hashlib
import os

import pytest

from vbr_devkit.download.transfer import DownloadError, fetch, part_path

DATA = os.urandom(3 * (1 << 20) + 123)  # spans several chunks
SHA = hashlib.sha256(DATA).hexdigest()


@pytest.fixture
def remote(server):
    server.files["/seq/file.bag"] = DATA
    return server, server.url + "/seq/file.bag"


def test_full_download(remote, tmp_path):
    _, url = remote
    dest = tmp_path / "out" / "file.bag"
    seen = []
    fetch(url, dest, len(DATA), SHA, backoff=0, on_progress=seen.append)
    assert dest.read_bytes() == DATA
    assert not part_path(dest).exists()
    assert seen[-1] == len(DATA)


def test_resume_from_part(remote, tmp_path):
    server, url = remote
    dest = tmp_path / "file.bag"
    part_path(dest).write_bytes(DATA[:1000])
    fetch(url, dest, len(DATA), SHA, backoff=0)
    assert dest.read_bytes() == DATA
    assert server.requests == [("/seq/file.bag", "bytes=1000-")]


def test_server_ignoring_range_restarts(remote, tmp_path):
    server, url = remote
    server.support_range = False
    dest = tmp_path / "file.bag"
    part_path(dest).write_bytes(b"x" * 1000)  # garbage must be overwritten
    fetch(url, dest, len(DATA), SHA, backoff=0)
    assert dest.read_bytes() == DATA


def test_retry_on_server_error(remote, tmp_path):
    server, url = remote
    server.fail_next = [503, 502]
    dest = tmp_path / "file.bag"
    fetch(url, dest, len(DATA), SHA, backoff=0)
    assert dest.read_bytes() == DATA
    assert len(server.requests) == 3


def test_truncated_transfer_resumes(remote, tmp_path):
    server, url = remote
    server.truncate_next = 1
    dest = tmp_path / "file.bag"
    fetch(url, dest, len(DATA), SHA, backoff=0)
    assert dest.read_bytes() == DATA
    assert server.requests[0][1] is None
    assert server.requests[1][1] is not None and server.requests[1][1] != "bytes=0-"


def test_part_already_complete(remote, tmp_path):
    server, url = remote
    dest = tmp_path / "file.bag"
    part_path(dest).write_bytes(DATA)
    fetch(url, dest, len(DATA), SHA, backoff=0)
    assert dest.read_bytes() == DATA
    assert server.requests == []


def test_gives_up_after_retries(remote, tmp_path):
    server, url = remote
    server.fail_next = [503] * 10
    with pytest.raises(DownloadError):
        fetch(url, tmp_path / "file.bag", len(DATA), retries=2, backoff=0)
    assert len(server.requests) == 3


def test_not_found_is_permanent(server, tmp_path):
    with pytest.raises(DownloadError, match="404"):
        fetch(server.url + "/missing", tmp_path / "x", 10, backoff=0)
    assert len(server.requests) == 1


def test_checksum_mismatch(remote, tmp_path):
    _, url = remote
    dest = tmp_path / "file.bag"
    with pytest.raises(DownloadError, match="SHA-256"):
        fetch(url, dest, len(DATA), "0" * 64, backoff=0)
    assert not dest.exists() and not part_path(dest).exists()
