from __future__ import annotations

import os
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.shell.wrapper import resolve_shell_path

OFFICIAL_AIHUBSHELL_URL = "https://api.aihub.or.kr/api/aihubshell.do"


class InstallationError(RuntimeError):
    """Raised when installing aihubshell fails."""


@dataclass(slots=True)
class InstallResult:
    path: Path
    installed: bool
    verified: bool
    verification_output: str
    path_guidance: str | None = None


def default_install_path(settings: ScoutSettings) -> Path:
    if settings.aihub_shell_path is not None:
        return settings.aihub_shell_path
    return Path.home() / ".local" / "bin" / "aihubshell"


def _download_official_shell() -> str:
    request = Request(
        OFFICIAL_AIHUBSHELL_URL,
        headers={"User-Agent": "aihub-korea-metadata-scout/0.1.0"},
    )
    try:
        with urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8")
    except HTTPError as exc:
        msg = f"Official aihubshell download failed with HTTP {exc.code}: {OFFICIAL_AIHUBSHELL_URL}"
        raise InstallationError(msg) from exc
    except URLError as exc:
        msg = (
            "Could not reach the official aihubshell endpoint. "
            "Check network access to https://api.aihub.or.kr."
        )
        raise InstallationError(msg) from exc


def _path_guidance(target: Path) -> str | None:
    path_dirs = {Path(item).expanduser().resolve() for item in os_path_entries()}
    if target.parent.resolve() in path_dirs:
        return None
    return (
        f"`{target.parent}` is not currently on PATH. Add "
        f'`export PATH="{target.parent}:$PATH"` to your shell profile.'
    )


def os_path_entries() -> list[str]:
    return [item for item in os.environ.get("PATH", "").split(":") if item]


def install_aihubshell(settings: ScoutSettings, force: bool = False) -> InstallResult:
    target = default_install_path(settings)
    target.parent.mkdir(parents=True, exist_ok=True)

    should_install = force or not target.exists()
    if should_install:
        try:
            script_text = _download_official_shell()
            target.write_text(script_text, encoding="utf-8")
        except PermissionError as exc:
            msg = (
                f"Cannot write aihubshell to {target}. Choose a writable location with "
                "`AIHUB_SHELL_PATH` or use the default user-local target."
            )
            raise InstallationError(msg) from exc
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    try:
        completed = subprocess.run(
            [str(target), "-mode", "l"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            check=False,
        )
    except OSError as exc:
        msg = f"Installed aihubshell is not executable: {target}"
        raise InstallationError(msg) from exc

    if completed.returncode != 0:
        snippet = (completed.stdout + "\n" + completed.stderr).strip()
        msg = f"aihubshell installed at {target} but verification failed:\n{snippet}"
        raise InstallationError(msg)

    return InstallResult(
        path=target,
        installed=should_install,
        verified=True,
        verification_output=completed.stdout.strip(),
        path_guidance=_path_guidance(target),
    )


def describe_shell_status(settings: ScoutSettings) -> tuple[bool, Path | None]:
    resolved = resolve_shell_path(settings)
    return (resolved is not None and resolved.exists(), resolved)
