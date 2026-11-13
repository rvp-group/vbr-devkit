# Changelog

## Unreleased

### Added
- `vbr --version` (`-V`) prints the installed version.

## 1.0.0

### Changed
- `vbr download` now fetches data over HTTPS from `https://www.diag.uniroma1.it/<sequence>/<file>`.
  The anonymous FTP server is no longer available.
- The list of files (with sizes and optional SHA-256 checksums) is bundled in the package
  (`vbr_devkit/download/manifest.json`), regenerated with `scripts/build_manifest.py`.
- `vbr download` exits with a non-zero status if any file failed.

### Added
- Resumable downloads (HTTP Range requests) with automatic retries; re-running the same command
  continues where it stopped and skips files already downloaded.
- `--only {calib,gt,bags}`, `--dry-run`, `--skip-existing/--no-skip-existing`, `--verify/--no-verify`.
- `VBR_BASE_URL` environment variable to override the download server.
- Update check: at most once a day `vbr` queries PyPI (2 s timeout, silent on errors) and warns on
  stderr when a newer release exists. Disable with `VBR_NO_UPDATE_CHECK=1`.
- Test suite (`pytest python/tests`).

### Removed
- FTP download code (`ftplib`).
