from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from aihub_korea_metadata_scout.config import ConfigurationError, ScoutSettings
from aihub_korea_metadata_scout.models import CommandTrace, sha256_text


class ShellExecutionError(RuntimeError):
    """Raised when the official aihubshell cannot be executed successfully."""


@dataclass(slots=True)
class ShellExecution:
    executable: Path
    stdout: str
    stderr: str
    trace: CommandTrace


def resolve_shell_path(settings: ScoutSettings) -> Path | None:
    """Resolve the official aihubshell path from override, PATH, or user-local install."""

    if settings.aihub_shell_path is not None:
        return settings.aihub_shell_path

    in_path = shutil.which("aihubshell")
    if in_path:
        return Path(in_path).resolve()

    user_local = Path.home() / ".local" / "bin" / "aihubshell"
    if user_local.exists():
        return user_local
    return None


class AIHubShellWrapper:
    """Thin subprocess wrapper around the official aihubshell executable."""

    def __init__(self, settings: ScoutSettings):
        self.settings = settings

    def require_executable(self) -> Path:
        executable = resolve_shell_path(self.settings)
        if executable is None:
            msg = (
                "Could not find `aihubshell`. Run `make bootstrap` or "
                "`aihub-korea-scout bootstrap` first."
            )
            raise ConfigurationError(msg)
        if not executable.exists():
            msg = f"Resolved aihubshell path does not exist: {executable}"
            raise ConfigurationError(msg)
        if not os.access(executable, os.X_OK):
            msg = f"Resolved aihubshell path is not executable: {executable}"
            raise ConfigurationError(msg)
        return executable

    def run(self, args: list[str], timeout: int = 90, check: bool = True) -> ShellExecution:
        executable = self.require_executable()
        command = [str(executable), *args]
        env = os.environ.copy()
        if self.settings.aihub_api_key:
            env.setdefault("AIHUB_APIKEY", self.settings.aihub_api_key)
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
        trace = CommandTrace(
            executable=str(executable),
            args=args,
            command=shlex.join(command),
            exit_code=completed.returncode,
            collected_at=datetime.now(UTC),
            stdout_sha256=sha256_text(completed.stdout),
            stderr=completed.stderr.strip(),
        )
        execution = ShellExecution(
            executable=executable,
            stdout=completed.stdout,
            stderr=completed.stderr,
            trace=trace,
        )
        if check and completed.returncode != 0:
            msg = (
                f"aihubshell command failed with exit code {completed.returncode}: "
                f"{trace.command}\n{completed.stderr.strip()}"
            )
            raise ShellExecutionError(msg)
        return execution

    def verify_metadata_access(self) -> ShellExecution:
        return self.run(["-mode", "l"], timeout=120, check=True)
