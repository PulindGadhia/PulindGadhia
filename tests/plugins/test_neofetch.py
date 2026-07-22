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
from github_profiler.application.plugins.neofetch import NeofetchPlugin
from github_profiler.domain.components import (
    Canvas,
    ComponentGroup,
    ComponentText,
    Dashboard,
)
from github_profiler.domain.geometry import Padding
from github_profiler.domain.interfaces import IGitHubClient
from github_profiler.domain.models import GitHubUser, ProfileStats
from github_profiler.domain.theme import Theme
from github_profiler.infrastructure.cache import LocalFSCache
from github_profiler.infrastructure.dashboard_renderer import DashboardRenderer
from github_profiler.infrastructure.plugin_loader import FilesystemPluginLoader
from github_profiler.infrastructure.rendering import SVGEngine


def test_neofetch_unit() -> None:
    """1. Domain tests: returns Canvas, measure() unchanged."""
    plugin = NeofetchPlugin()
    stats = ProfileStats(total_repositories=2)
    user = GitHubUser(
        username="octocat",
        name=None,
        bio=None,
        company=None,
        location=None,
        followers=10,
        following=5,
        stats=stats,
        avatar_url="",
    )
    theme = Theme()

    canvas = plugin.generate(user, theme)
    assert isinstance(canvas, Canvas)
    assert len(canvas.children) == 8  # 1 bg + 7 lines

    text_comp = canvas.children[1]
    assert isinstance(text_comp, ComponentText)
    assert text_comp.content == "octocat@github"


def test_neofetch_snapshot() -> None:
    plugin = NeofetchPlugin()
    stats = ProfileStats(total_repositories=1)
    user = GitHubUser(
        username="test",
        name=None,
        bio=None,
        company=None,
        location=None,
        followers=1,
        following=1,
        stats=stats,
        avatar_url="",
    )
    theme = Theme()
    canvas = plugin.generate(user, theme)

    assert isinstance(canvas, Canvas)
    lines = [
        child.content
        for child in canvas.children
        if isinstance(child, ComponentText)
    ]
    assert lines == [
        "test@github",
        "-----------",
        "OS: GitHub Profile",
        "Host: github.com/test",
        "Followers: 1",
        "Following: 1",
        "Repos: 1",
    ]


def test_neofetch_benchmark() -> None:
    plugin = NeofetchPlugin()
    user = GitHubUser(
        username="speedy",
        name=None,
        bio=None,
        company=None,
        location=None,
        followers=0,
        following=0,
        avatar_url="",
    )
    theme = Theme()

    start = time.perf_counter()
    for _ in range(1000):
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
        )


def test_neofetch_dashboard_integration(tmp_path: Path) -> None:
    """2. Layout tests: Card wrapping, Canvas translation."""
    config_file = tmp_path / "profile.toml"
    config_file.write_text('plugins = ["neofetch"]')

    config_mgr = ConfigManager(config_file)
    plugin_mgr = PluginManager(FilesystemPluginLoader())
    gen_service = DashboardGenerationService(
        MockGitHubClient(), LocalFSCache(tmp_path), DashboardRenderer()
    )
    orchestrator = DashboardOrchestrator(
        config_mgr, plugin_mgr, gen_service, EventBus()
    )

    svg = orchestrator.build_profile("integrator")
    assert "integrator@github" in svg


def test_neofetch_migration_parity() -> None:
    """3. Rendering tests: SVG parity with legacy."""
    plugin = NeofetchPlugin()
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

    legacy_texts = legacy_root.findall(".//svg:text", ns)
    dash_texts = dash_root.findall(".//svg:text", ns)

    assert len(legacy_texts) == len(dash_texts)
    assert len(legacy_texts) > 0
    for legacy_text, dash_text in zip(legacy_texts, dash_texts):
        assert legacy_text.attrib["x"] == dash_text.attrib["x"]
        assert legacy_text.attrib["y"] == dash_text.attrib["y"]
        assert legacy_text.text == dash_text.text


def test_neofetch_legacy_failure(tmp_path: Path) -> None:
    """4. Failure test: Attempt to pass Canvas through legacy ProfileOrchestrator."""
    config_file = tmp_path / "profile.toml"
    config_file.write_text('plugins = ["neofetch"]')

    config_mgr = ConfigManager(config_file)
    plugin_mgr = PluginManager(FilesystemPluginLoader())
    gen_service = GenerationService(
        MockGitHubClient(), LocalFSCache(tmp_path), SVGEngine()
    )
    orchestrator = ProfileOrchestrator(
        config_mgr, plugin_mgr, gen_service, EventBus()
    )

    with pytest.raises(RuntimeError) as exc_info:
        orchestrator.build_profile("integrator")

    assert "requires the 'dashboard' pipeline" in str(
        exc_info.value
    )
