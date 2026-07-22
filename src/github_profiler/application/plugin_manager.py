"""Plugin Manager implementation."""

from typing import List

from github_profiler.domain.interfaces import IPluginLoader, IProfilePlugin


class PluginManager:
    """Orchestrates plugin loading."""

    def __init__(self, loader: IPluginLoader) -> None:
        """Initializes with an infrastructure loader."""
        self.loader = loader

    def get_plugins(self, names: List[str], expected_pipeline: str = "legacy") -> List[IProfilePlugin]:
        """Loads and returns requested plugins.

        Args:
            names: List of plugin identifiers.
            expected_pipeline: The pipeline required by the caller.

        Returns:
            List of instantiated plugins.
        """
        plugins = self.loader.load_plugins(names)
        for plugin in plugins:
            if plugin.pipeline != expected_pipeline:
                raise RuntimeError(
                    f"Plugin '{plugin.name}' requires the '{plugin.pipeline}' pipeline, "
                    f"but was loaded in a '{expected_pipeline}' orchestrator."
                )
        return plugins
