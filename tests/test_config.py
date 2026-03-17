from __future__ import annotations

import pytest

from aihub_korea_metadata_scout.config import ConfigurationError, ScoutSettings


def test_validate_python_version_accepts_supported_versions() -> None:
    ScoutSettings.validate_python_version((3, 11, 0))
    ScoutSettings.validate_python_version((3, 12, 5))


def test_validate_python_version_rejects_unsupported_versions() -> None:
    with pytest.raises(ConfigurationError, match=r"Python 3\.11\+ is required"):
        ScoutSettings.validate_python_version((3, 10, 12))


def test_format_python_version_returns_dotted_string() -> None:
    assert ScoutSettings.format_python_version((3, 11, 15)) == "3.11.15"
