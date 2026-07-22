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
    """Legacy profile generation pipeline."""
    
    _warned = False

    def __init__(
        self,
        github_client: IGitHubClient,
        cache: ICache,
        renderer: IComponentRenderer,
    ) -> None:
        if not GenerationService._warned:
            import warnings
            warnings.warn("GenerationService is deprecated and will be removed in v3.1.", DeprecationWarning, stacklevel=2)
            GenerationService._warned = True
        self.github = github_client
        self.cache = cache
        self.renderer = renderer


class ProfileOrchestrator:
    """Legacy facade for rendering standard profiles."""
    
    _warned = False

    def __init__(
        self,
        config: ConfigManager,
        plugins: PluginManager,
        gen: GenerationService,
        events: IEventBus,
    ) -> None:
        if not ProfileOrchestrator._warned:
            import warnings
            warnings.warn("ProfileOrchestrator is deprecated and will be removed in v3.1.", DeprecationWarning, stacklevel=2)
            ProfileOrchestrator._warned = True
        self.config = config
        self.plugins = plugins
        self.gen = gen
        self.events = events

    def build_profile(self, username: str) -> str:
        """Executes the full pipeline to generate the SVG profile."""

        # ------------------------------------------------------------------
        # 1. Fetch User Data
        # ------------------------------------------------------------------
        self.events.publish(Event("pre_fetch", {"username": username}))

        # Check cache first
        user = self.gen.cache.get(f"user_{username}")
        if not user:
            user = self.gen.github.fetch_user_data(username)
            self.gen.cache.set(f"user_{username}", user)

        self.events.publish(Event("post_fetch", {"user": user}))

        # ------------------------------------------------------------------
        # 2. Load Theme & Plugins
        # ------------------------------------------------------------------
        theme = self.config.get_theme()
        plugin_names = self.config.get_plugins()
        active_plugins = self.plugins.get_plugins(plugin_names)

        # ------------------------------------------------------------------
        # 3. Generate Components
        # ------------------------------------------------------------------
        components: List[UIComponent] = []

        for plugin in active_plugins:
            component = plugin.generate(user, theme)
            components.append(component)

        self.events.publish(
            Event(
                "pre_render",
                {"components": components},
            )
        )

        # ------------------------------------------------------------------
        # 4. Render Final SVG
        # ------------------------------------------------------------------
        result = self.gen.renderer.render(
            components,
            theme,
        )

        self.events.publish(
            Event(
                "post_render",
                {"length": len(result)},
            )
        )

        return result