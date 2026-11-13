from typer.testing import CliRunner

from vbr_devkit.tools import update_check
from vbr_devkit.tools.run import app

runner = CliRunner()


def test_version(monkeypatch):
    monkeypatch.setenv(update_check.DISABLE_ENV, "1")
    for flag in ("--version", "-V"):
        result = runner.invoke(app, [flag])
        assert result.exit_code == 0
        assert result.output.strip() == f"vbr-devkit {update_check.installed_version()}"
