"""Core profile orchestration and generation."""

from typing import List

from github_profiler.application.config_manager import ConfigManager
from github_profiler.application.plugin_manager import PluginManager
from github_profiler.domain.components import UIComponent
from github_profiler.domain.events import Event
from github_profiler.domain.interfaces import (
    ICache,
    IComponentRenderer,
    IEventBus,
    IGitHubClient,
)


class GenerationService:
    """Core domain logic wrapper."""

    def __init__(
        self, github: IGitHubClient, cache: ICache, renderer: IComponentRenderer
    ) -> None:
        self.github = github
        self.cache = cache
        self.renderer = renderer


class ProfileOrchestrator:
    """High-level profile builder."""

    def __init__(
        self,
        config_mgr: ConfigManager,
        plugin_mgr: PluginManager,
        gen_service: GenerationService,
        event_bus: IEventBus,
    ) -> None:
        self.config = config_mgr
        self.plugins = plugin_mgr
        self.gen = gen_service
        self.events = event_bus

    def build_profile(self, username: str) -> str:
        """Executes the full pipeline to generate the SVG profile."""

        # 1. Fetch User Data
        self.events.publish(Event("pre_fetch", {"username": username}))

        # Check cache first
        user = self.gen.cache.get(f"user_{username}")
        if not user:
            user = self.gen.github.fetch_user_data(username)
            self.gen.cache.set(f"user_{username}", user)

        self.events.publish(Event("post_fetch", {"user": user}))

        # 2. Load Config & Plugins
        theme = self.config.get_theme()
        plugin_names = self.config.get_plugins()
        active_plugins = self.plugins.get_plugins(plugin_names)

        # 3. Generate Components
        components: List[UIComponent] = []
        for p in active_plugins:
            components.append(p.generate(user, theme))

        self.events.publish(Event("pre_render", {"components": components}))

        # 4. Render Final SVG
        result = self.gen.renderer.render(components, theme)

        self.events.publish(Event("post_render", {"length": len(result)}))
        return result
