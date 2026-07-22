import datetime
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from github_profiler.application.config_manager import ConfigManager
from github_profiler.application.dashboard_orchestrator import (
    DashboardGenerationService,
    DashboardOrchestrator,
)
from github_profiler.application.event_bus import EventBus
from github_profiler.application.orchestrator import (
    GenerationService,
    ProfileOrchestrator,
)
from github_profiler.application.plugin_manager import PluginManager
from github_profiler.application.plugins.heatmap import HeatmapPlugin
from github_profiler.domain.components import Canvas, ComponentBox, ComponentGroup, Dashboard
from github_profiler.domain.geometry import Padding
from github_profiler.domain.interfaces import IGitHubClient
from github_profiler.domain.models import ContributionDay, GitHubUser, ProfileStats
from github_profiler.domain.theme import Theme
from github_profiler.infrastructure.cache import LocalFSCache
from github_profiler.infrastructure.dashboard_renderer import DashboardRenderer
from github_profiler.infrastructure.plugin_loader import FilesystemPluginLoader
from github_profiler.infrastructure.rendering import SVGEngine


def _generate_mock_calendar(days: int = 10) -> list[ContributionDay]:
    base = datetime.date(2023, 1, 1)
    return [
        ContributionDay(
            date=base + datetime.timedelta(days=i),
            contribution_count=i % 3,
            color="#00ff00",
        )
        for i in range(days)
    ]


def test_heatmap_unit() -> None:
    """1. Domain test for Heatmap generation logic."""
    plugin = HeatmapPlugin()
    calendar = _generate_mock_calendar(10)
    user = GitHubUser(
        username="octocat",
        name=None,
        bio=None,
        company=None,
        location=None,
        avatar_url="",
        followers=0,
        following=0,
        contribution_calendar=calendar,
        stats=ProfileStats(total_repositories=0)
    )
    theme = Theme()

    comp = plugin.generate(user, theme)
    assert isinstance(comp, Canvas)
    assert len(comp.children) == 11

    bg = comp.children[0]
    assert isinstance(bg, ComponentBox)
    assert getattr(bg, "width") > 0

    first_cell = comp.children[1]
    assert isinstance(first_cell, ComponentBox)
    assert getattr(first_cell, "fill_color") == theme.palette.secondary
    assert getattr(first_cell, "attributes")["title"] == "0 contributions on 2023-01-01"


def test_heatmap_snapshot() -> None:
    """Snapshot test verifying layout coordinates and spacing."""
    plugin = HeatmapPlugin()
    calendar = _generate_mock_calendar(8)
    user = GitHubUser(
        username="test",
        name=None,
        bio=None,
        company=None,
        location=None,
        avatar_url="",
        followers=0,
        following=0,
        contribution_calendar=calendar,
        stats=ProfileStats(total_repositories=0)
    )
    theme = Theme()
    comp = plugin.generate(user, theme)

    assert isinstance(comp, Canvas)
    cell1 = comp.children[1]
    cell8 = comp.children[8]

    assert getattr(cell1, "x") == 4
    assert getattr(cell1, "y") == 4

    assert getattr(cell8, "x") == 18
    assert getattr(cell8, "y") == 4


def test_heatmap_benchmark() -> None:
    """Performance benchmark for Heatmap generation."""
    plugin = HeatmapPlugin()
    calendar = _generate_mock_calendar(365)
    user = GitHubUser(
        username="speedy",
        name=None,
        bio=None,
        company=None,
        location=None,
        avatar_url="",
        followers=0,
        following=0,
        contribution_calendar=calendar,
        stats=ProfileStats(total_repositories=0)
    )
    theme = Theme()

    start = time.perf_counter()
    for _ in range(100):
        plugin.generate(user, theme)
    duration = time.perf_counter() - start
    assert duration < 0.5


class MockGitHubClient(IGitHubClient):
    def fetch_user_data(self, username: str) -> GitHubUser:
        stats = ProfileStats(total_repositories=3)
        return GitHubUser(
            username=username,
            name=None,
            bio=None,
            company=None,
            location=None,
            followers=1,
            following=2,
            stats=stats,
            avatar_url="",
            contribution_calendar=_generate_mock_calendar(3),
        )


def test_heatmap_dashboard_integration(tmp_path: Path) -> None:
    """2. Layout test: Integration with DashboardOrchestrator."""
    config_file = tmp_path / "profile.toml"
    config_file.write_text('plugins = ["heatmap"]')

    config_mgr = ConfigManager(config_file)
    plugin_mgr = PluginManager(FilesystemPluginLoader())
    gen_service = DashboardGenerationService(
        MockGitHubClient(), LocalFSCache(tmp_path), DashboardRenderer()
    )
    orchestrator = DashboardOrchestrator(config_mgr, plugin_mgr, gen_service, EventBus())

    svg = orchestrator.build_profile("integrator")
    assert "data-tooltip" in svg


def test_heatmap_migration_parity() -> None:
    """3. Rendering test: SVG parity with legacy."""
    plugin = HeatmapPlugin()
    user = MockGitHubClient().fetch_user_data("test")
    theme = Theme()

    canvas = plugin.generate(user, theme)
    assert isinstance(canvas, Canvas)
    
    # Legacy Engine SVG
    legacy_group = ComponentGroup(x=canvas.x, y=canvas.y)
    legacy_group.children = canvas.children
    legacy_engine = SVGEngine()
    legacy_svg = legacy_engine.render([legacy_group], theme)

    # Dashboard Engine SVG
    dash = Dashboard(children=[canvas], gap=0)
    dash.padding = Padding.all(0)
    dashboard_engine = DashboardRenderer()
    dashboard_svg = dashboard_engine.render(dash, theme)

    ns = {"svg": "http://www.w3.org/2000/svg"}
    legacy_root = ET.fromstring(legacy_svg)
    dash_root = ET.fromstring(dashboard_svg)

    legacy_rects = legacy_root.findall(".//svg:rect", ns)
    dash_rects = dash_root.findall(".//svg:rect", ns)
    
    # Filter out the root background rect
    legacy_rects = [r for r in legacy_rects if r.attrib.get("width") != "100%"]
    dash_rects = [r for r in dash_rects if r.attrib.get("width") != "100%"]
    
    assert len(legacy_rects) == len(dash_rects)
    assert len(legacy_rects) > 0
    
    for legacy_rect, dash_rect in zip(legacy_rects, dash_rects):
        assert legacy_rect.attrib["x"] == dash_rect.attrib["x"]
        assert legacy_rect.attrib["y"] == dash_rect.attrib["y"]
        assert legacy_rect.attrib["width"] == dash_rect.attrib["width"]
        assert legacy_rect.attrib["height"] == dash_rect.attrib["height"]


def test_heatmap_legacy_failure(tmp_path: Path) -> None:
    """4. Failure test: Pipeline compatibility rejection."""
    config_file = tmp_path / "profile.toml"
    config_file.write_text('plugins = ["heatmap"]')

    config_mgr = ConfigManager(config_file)
    plugin_mgr = PluginManager(FilesystemPluginLoader())
    gen_service = GenerationService(
        MockGitHubClient(), LocalFSCache(tmp_path), SVGEngine()
    )
    # This orchestrator uses the legacy rendering pipeline, but heatmap requires 'dashboard'
    # Actually, the PluginManager will fail immediately!
    orchestrator = ProfileOrchestrator(config_mgr, plugin_mgr, gen_service, EventBus())

    with pytest.raises(RuntimeError) as exc_info:
        orchestrator.build_profile("integrator")
        
    assert "requires the 'dashboard' pipeline" in str(exc_info.value)
