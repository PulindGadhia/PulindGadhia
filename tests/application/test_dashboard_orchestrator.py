from unittest.mock import MagicMock

from github_profiler.application.config_manager import ConfigManager
from github_profiler.application.dashboard_orchestrator import (
    DashboardGenerationService,
    DashboardOrchestrator,
)
from github_profiler.application.plugin_manager import PluginManager
from github_profiler.domain.components import Canvas, Card, Column, Dashboard, Row
from github_profiler.domain.interfaces import (
    ICache,
    IDashboardRenderer,
    IEventBus,
    IGitHubClient,
)


def test_dashboard_orchestrator_tree_construction() -> None:
    # Mocks
    mock_config = MagicMock(spec=ConfigManager)
    mock_config.get_plugins.return_value = ["ascii_portrait", "neofetch", "heatmap"]

    # Mock plugins returning Canvas
    plugin_ascii = MagicMock()
    plugin_ascii.name = "ascii_portrait"
    plugin_ascii.generate.return_value = Canvas(width=100, height=100)

    plugin_neofetch = MagicMock()
    plugin_neofetch.name = "neofetch"
    plugin_neofetch.generate.return_value = Canvas(width=150, height=150)

    plugin_heatmap = MagicMock()
    plugin_heatmap.name = "heatmap"
    plugin_heatmap.generate.return_value = Canvas(width=800, height=150)

    mock_plugins = MagicMock(spec=PluginManager)
    mock_plugins.get_plugins.return_value = [
        plugin_ascii,
        plugin_neofetch,
        plugin_heatmap,
    ]

    mock_renderer = MagicMock(spec=IDashboardRenderer)
    mock_renderer.render.return_value = "<svg></svg>"

    mock_github = MagicMock(spec=IGitHubClient)
    mock_cache = MagicMock(spec=ICache)
    mock_cache.get.return_value = MagicMock()

    gen_service = DashboardGenerationService(
        github=mock_github,
        cache=mock_cache,
        renderer=mock_renderer,
    )

    mock_events = MagicMock(spec=IEventBus)

    orchestrator = DashboardOrchestrator(
        config_mgr=mock_config,
        plugin_mgr=mock_plugins,
        gen_service=gen_service,
        event_bus=mock_events,
    )

    svg = orchestrator.build_profile("test_user")
    assert svg == "<svg></svg>"

    # 1. Renderer is called exactly once
    mock_renderer.render.assert_called_once()

    # Extract the dashboard argument passed to render
    args, kwargs = mock_renderer.render.call_args
    dashboard = args[0]

    # 2. Dashboard tree construction
    assert isinstance(dashboard, Dashboard)

    # Dashboard -> Column
    assert len(dashboard.children) == 1
    col = dashboard.children[0]
    assert isinstance(col, Column)

    # Column -> [Row, Card(Heatmap)]
    assert len(col.children) == 2
    row = col.children[0]
    assert isinstance(row, Row)
    heatmap_card = col.children[1]
    assert isinstance(heatmap_card, Card)

    # Row -> [Card(Ascii), Card(Neofetch)]
    assert len(row.children) == 2
    ascii_card = row.children[0]
    neo_card = row.children[1]

    # 3. Correct plugin ordering
    assert isinstance(ascii_card, Card)
    assert isinstance(neo_card, Card)

    # 4. Cards wrap Canvases correctly
    assert ascii_card.content == plugin_ascii.generate.return_value
    assert neo_card.content == plugin_neofetch.generate.return_value
    assert heatmap_card.content == plugin_heatmap.generate.return_value


def test_dashboard_orchestrator_imports() -> None:
    """Verifies that the orchestrator does NOT import layout engine or SVG builder."""
    with open(
        "src/github_profiler/application/dashboard_orchestrator.py", "r"
    ) as f:
        content = f.read()

    assert "DashboardLayoutEngine" not in content
    assert "SVGBuilder" not in content
