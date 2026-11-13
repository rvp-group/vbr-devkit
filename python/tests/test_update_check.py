import json

import pytest

from vbr_devkit.tools import update_check as uc


@pytest.fixture
def pypi(server, tmp_path, monkeypatch):
    def publish(version):
        server.files["/pypi/vbr-devkit/json"] = json.dumps({"info": {"version": version}}).encode()

    monkeypatch.setattr(uc, "PYPI_URL", server.url + "/pypi/vbr-devkit/json")
    monkeypatch.setattr(uc, "installed_version", lambda: "1.0.0")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.delenv(uc.DISABLE_ENV, raising=False)
    return publish


def test_newer_version_warns(pypi, capsys):
    pypi("1.1.0")
    assert uc.newer_version_available() == "1.1.0"
    uc.warn_if_outdated()
    err = capsys.readouterr().err
    assert "1.1.0" in err and "pip install -U vbr-devkit" in err


@pytest.mark.parametrize("latest", ["1.0.0", "0.9.9", "2.0.0rc1"])
def test_no_warning_when_not_newer(pypi, latest):
    pypi(latest)
    assert uc.newer_version_available() is None


def test_result_cached_for_a_day(pypi, server):
    pypi("1.1.0")
    assert uc.newer_version_available() == "1.1.0"
    assert uc.newer_version_available() == "1.1.0"
    assert len(server.requests) == 1
    assert uc.latest_version(now=__import__("time").time() + uc.CHECK_INTERVAL + 1) == "1.1.0"
    assert len(server.requests) == 2


def test_errors_are_silent(pypi, server):
    server.fail_next = [503]
    assert uc.newer_version_available() is None
    server.files.clear()  # 404
    assert uc.newer_version_available() is None


def test_disabled_by_env(pypi, server, monkeypatch):
    pypi("9.0.0")
    monkeypatch.setenv(uc.DISABLE_ENV, "1")
    assert uc.newer_version_available() is None
    assert server.requests == []


def test_parse_version():
    assert uc.parse_version("1.10.0") > uc.parse_version("1.9.3")
    assert uc.parse_version("1.0.0b1") is None
