"""V3 Dashboard Orchestrator and Generation Service."""

from typing import Dict, List

from github_profiler.application.config_manager import ConfigManager
from github_profiler.application.plugin_manager import PluginManager
from github_profiler.domain.components import Card, Column, Dashboard, Row, UIComponent
from github_profiler.domain.events import Event
from github_profiler.domain.interfaces import (
    ICache,
    IDashboardRenderer,
    IEventBus,
    IGitHubClient,
)


class DashboardGenerationService:
    """Core domain logic wrapper for V3 architecture."""

    def __init__(
        self,
        github: IGitHubClient,
        cache: ICache,
        renderer: IDashboardRenderer,
    ) -> None:
        self.github = github
        self.cache = cache
        self.renderer = renderer


class DashboardOrchestrator:
    """High-level profile builder explicitly mapping plugins to a Dashboard structure."""

    def __init__(
        self,
        config_mgr: ConfigManager,
        plugin_mgr: PluginManager,
        gen_service: DashboardGenerationService,
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

        user = self.gen.cache.get(f"user_{username}")
        if not user:
            user = self.gen.github.fetch_user_data(username)
            self.gen.cache.set(f"user_{username}", user)

        self.events.publish(Event("post_fetch", {"user": user}))

        # 2. Load Configuration
        theme = self.config.get_theme()
        plugin_names = self.config.get_plugins()
        active_plugins = self.plugins.get_plugins(plugin_names, expected_pipeline="dashboard")

        # 3. Execute Plugins and Wrap in Cards
        cards: Dict[str, Card] = {}
        for plugin in active_plugins:
            # Plugins are expected to return a Canvas in V3. 
            # We blindly wrap the UIComponent in a Card to decouple layout from plugins.
            component: UIComponent = plugin.generate(user, theme)
            cards[plugin.name] = Card(content=component, shadow=True)

        # 4. Build the Dashboard Tree explicitly
        row_children: List[UIComponent] = []
        if "ascii_portrait" in cards:
            row_children.append(cards["ascii_portrait"])
        if "neofetch" in cards:
            row_children.append(cards["neofetch"])
            
        row = Row(children=row_children)
        
        col_children: List[UIComponent] = [row] if row_children else []
        if "heatmap" in cards:
            col_children.append(cards["heatmap"])
            
        col = Column(children=col_children)
        dashboard = Dashboard(children=[col])

        self.events.publish(
            Event("pre_render", {"dashboard": dashboard})
        )

        # 5. Pass to Renderer
        result = self.gen.renderer.render(dashboard, theme)

        self.events.publish(
            Event("post_render", {"length": len(result)})
        )

        return result
