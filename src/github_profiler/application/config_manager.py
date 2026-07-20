"""Configuration Manager for merging env, TOML, and defaults."""


try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

from pathlib import Path
from typing import Any, Dict, List

from github_profiler.domain.theme import Theme


class ConfigManager:
    """Manages profile configuration precedence."""

    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path

    def load_config(self) -> Dict[str, Any]:
        """Loads the TOML configuration."""
        config: Dict[str, Any] = {}
        if self.config_path.exists():
            try:
                with open(self.config_path, "rb") as f:
                    config = tomllib.load(f)
            except Exception:
                pass
        return config

    def get_theme(self) -> Theme:
        """Returns the fully merged theme."""
        # For now, return default. In future, parse from config.
        return Theme()

    def get_plugins(self) -> List[str]:
        """Returns the list of plugins to execute."""
        config = self.load_config()
        return list(config.get("plugins", ["heatmap", "neofetch"]))
