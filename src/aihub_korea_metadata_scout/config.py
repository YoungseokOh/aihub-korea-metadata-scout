from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

MINIMUM_PYTHON_VERSION = (3, 11, 0)
MINIMUM_PYTHON_LABEL = "3.11+"


class ConfigurationError(RuntimeError):
    """Raised when local configuration is invalid for this application."""


def _resolve_path(path: Path) -> Path:
    expanded = path.expanduser()
    if expanded.is_absolute():
        return expanded
    return (Path.cwd() / expanded).resolve()


class ScoutSettings(BaseSettings):
    """Application settings loaded from environment variables and .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    aihub_api_key: str | None = Field(default=None, alias="AIHUB_API_KEY")
    aihub_shell_path: Path | None = Field(default=None, alias="AIHUB_SHELL_PATH")
    output_dir: Path = Field(default=Path("data"), alias="AIHUB_OUTPUT_DIR")
    cache_dir: Path | None = Field(default=None, alias="AIHUB_CACHE_DIR")

    @model_validator(mode="after")
    def normalize_paths(self) -> ScoutSettings:
        self.output_dir = _resolve_path(self.output_dir)
        self.cache_dir = (
            _resolve_path(self.cache_dir) if self.cache_dir else self.output_dir / "raw"
        )
        if self.aihub_shell_path is not None:
            self.aihub_shell_path = _resolve_path(self.aihub_shell_path)
        return self

    @property
    def raw_list_dir(self) -> Path:
        return self.cache_dir / "list"

    @property
    def raw_dataset_dir(self) -> Path:
        return self.cache_dir / "datasets"

    @property
    def normalized_dir(self) -> Path:
        return self.output_dir / "normalized"

    @property
    def normalized_list_dir(self) -> Path:
        return self.normalized_dir / "list"

    @property
    def normalized_dataset_dir(self) -> Path:
        return self.normalized_dir / "datasets"

    @property
    def normalized_scan_dir(self) -> Path:
        return self.normalized_dir / "scans"

    @property
    def generated_dir(self) -> Path:
        return self.output_dir / "generated"

    @property
    def generated_dataset_dir(self) -> Path:
        return self.generated_dir / "datasets"

    @property
    def generated_index_dir(self) -> Path:
        return self.generated_dir / "index"

    @property
    def catalog_json_path(self) -> Path:
        return self.normalized_dir / "catalog.json"

    @property
    def catalog_markdown_path(self) -> Path:
        return self.generated_index_dir / "dataset-catalog.md"

    def ensure_directories(self) -> None:
        directories = [
            self.output_dir,
            self.cache_dir,
            self.raw_list_dir,
            self.raw_dataset_dir,
            self.normalized_dir,
            self.normalized_list_dir,
            self.normalized_dataset_dir,
            self.normalized_scan_dir,
            self.generated_dir,
            self.generated_dataset_dir,
            self.generated_index_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def validate_paths(self) -> None:
        if (
            self.aihub_shell_path
            and self.aihub_shell_path.exists()
            and self.aihub_shell_path.is_dir()
        ):
            msg = (
                "AIHUB_SHELL_PATH points to a directory, not an executable: "
                f"{self.aihub_shell_path}"
            )
            raise ConfigurationError(msg)

    @staticmethod
    def current_python_version() -> tuple[int, int, int]:
        version_info = sys.version_info
        return (version_info.major, version_info.minor, version_info.micro)

    @staticmethod
    def format_python_version(version: tuple[int, int, int] | None = None) -> str:
        current_version = version or ScoutSettings.current_python_version()
        return ".".join(str(part) for part in current_version)

    @staticmethod
    def validate_python_version(version: tuple[int, int, int] | None = None) -> None:
        current_version = version or ScoutSettings.current_python_version()
        if current_version < MINIMUM_PYTHON_VERSION:
            msg = (
                f"Python {MINIMUM_PYTHON_LABEL} is required. Install it with "
                "`uv python install 3.11` and re-run `uv sync --python 3.11`."
            )
            raise ConfigurationError(msg)


@lru_cache(maxsize=1)
def get_settings() -> ScoutSettings:
    settings = ScoutSettings()
    settings.validate_paths()
    return settings


def reset_settings_cache() -> None:
    get_settings.cache_clear()
