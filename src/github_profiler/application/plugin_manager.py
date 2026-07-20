"""Plugin Manager implementation."""

from typing import List

from github_profiler.domain.interfaces import IPluginLoader, IProfilePlugin


class PluginManager:
    """Orchestrates plugin loading."""

    def __init__(self, loader: IPluginLoader) -> None:
        """Initializes with an infrastructure loader."""
        self.loader = loader

    def get_plugins(self, names: List[str]) -> List[IProfilePlugin]:
        """Loads and returns requested plugins.

        Args:
            names: List of plugin identifiers.

        Returns:
            List of instantiated plugins.
        """
        return self.loader.load_plugins(names)
