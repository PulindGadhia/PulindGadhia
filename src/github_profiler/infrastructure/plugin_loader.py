"""Filesystem-based plugin discovery."""

import importlib
from typing import List

from github_profiler.domain.interfaces import IPluginLoader, IProfilePlugin


class FilesystemPluginLoader(IPluginLoader):
    """Loads plugins dynamically from python modules."""

    def load_plugins(self, plugin_names: List[str]) -> List[IProfilePlugin]:
        plugins = []
        for name in plugin_names:
            try:
                # For built-in plugins, we look in application.plugins
                # Users could theoretically pass absolute module paths later.
                module_path = f"github_profiler.application.plugins.{name}"
                module = importlib.import_module(module_path)

                # We expect the module to expose a get_plugin factory method
                if hasattr(module, "get_plugin"):
                    plugin = module.get_plugin()
                    plugins.append(plugin)
            except ImportError:
                # For now, silently skip missing plugins.
                # In a robust system, this should log a warning.
                pass
        return plugins
