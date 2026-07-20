"""
Centralized configuration management for the GitHub Profile Generator.

This module provides immutable, validated configuration objects shared
throughout the application.

Features
--------
- Python 3.11+
- Dataclasses with slots
- pathlib everywhere
- Automatic directory creation
- Environment variable support
- Runtime validation
- Singleton configuration loader
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .exceptions import ConfigurationError, EnvironmentVariableError

# ---------------------------------------------------------------------
# Project Paths
# ---------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[2]

ASSETS_DIR = ROOT_DIR / "assets"
DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = ROOT_DIR / "docs"
OUTPUT_DIR = ROOT_DIR / "output"
TESTS_DIR = ROOT_DIR / "tests"

FONTS_DIR = ASSETS_DIR / "fonts"

PROFILE_IMAGE = ASSETS_DIR / "profile.jpg"

README_FILE = ROOT_DIR / "README.md"

# ---------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class GitHubConfig:
    """GitHub API configuration."""

    username: str
    token: str | None
    api_url: str = "https://api.github.com"

    @property
    def authenticated(self) -> bool:
        return bool(self.token)


# ---------------------------------------------------------------------
# ASCII
# ---------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class ASCIIConfig:
    """ASCII rendering configuration."""

    width: int = 100
    invert: bool = False
    charset: str = (
        "@%#*+=-:. "
    )


# ---------------------------------------------------------------------
# SVG
# ---------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class SVGConfig:
    """SVG rendering settings."""

    width: int = 1200
    height: int = 650

    background: str = "#0d1117"
    foreground: str = "#c9d1d9"

    font_family: str = "JetBrains Mono"

    font_size: int = 12

    cursor_color: str = "#58a6ff"

    fps: int = 60


# ---------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class AnimationConfig:
    """Animation settings."""

    typing_speed: float = 0.025

    blink_speed: float = 0.45

    loop: bool = True

    duration: float = 15.0


# ---------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class HeatmapConfig:
    """Contribution heatmap configuration."""

    cell_size: int = 11

    cell_gap: int = 2

    weeks: int = 53

    radius: int = 2


# ---------------------------------------------------------------------
# Information Card
# ---------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class InfoCardConfig:
    """Terminal card configuration."""

    terminal_width: int = 80

    avatar_size: int = 120

    accent_color: str = "#58A6FF"


# ---------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class ProjectConfig:
    """Root project configuration."""

    github: GitHubConfig

    ascii: ASCIIConfig

    svg: SVGConfig

    animation: AnimationConfig

    heatmap: HeatmapConfig

    info_card: InfoCardConfig


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def _ensure_directories() -> None:
    """Create required directories if they do not exist."""

    directories = (
        DATA_DIR,
        OUTPUT_DIR,
        DOCS_DIR,
        TESTS_DIR,
        ASSETS_DIR,
        FONTS_DIR,
    )

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def _load_github() -> GitHubConfig:
    """Load GitHub configuration."""

    username = os.getenv("GITHUB_USERNAME")

    if not username:
        raise EnvironmentVariableError(
            "GITHUB_USERNAME environment variable is required."
        )

    token = os.getenv("GITHUB_TOKEN")

    return GitHubConfig(
        username=username,
        token=token,
    )


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


@lru_cache(maxsize=1)
def get_config() -> ProjectConfig:
    """
    Return the singleton project configuration.

    Returns
    -------
    ProjectConfig
        Immutable configuration object.
    """

    _ensure_directories()

    if not PROFILE_IMAGE.exists():
        raise ConfigurationError(
            f"Profile image not found: {PROFILE_IMAGE}"
        )

    return ProjectConfig(
        github=_load_github(),
        ascii=ASCIIConfig(),
        svg=SVGConfig(),
        animation=AnimationConfig(),
        heatmap=HeatmapConfig(),
        info_card=InfoCardConfig(),
    )