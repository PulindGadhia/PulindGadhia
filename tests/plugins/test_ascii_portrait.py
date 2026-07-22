import io
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from github_profiler.application.config_manager import ConfigManager
from github_profiler.application.dashboard_orchestrator import DashboardOrchestrator, DashboardGenerationService
from github_profiler.application.event_bus import EventBus
from github_profiler.application.plugin_manager import PluginManager
from github_profiler.application.plugins.ascii_portrait import AsciiPortraitPlugin
from github_profiler.domain.components import Canvas, ComponentGroup, Dashboard
from github_profiler.domain.geometry import Padding
from github_profiler.domain.interfaces import IGitHubClient
from github_profiler.domain.models import GitHubUser, ProfileStats
from github_profiler.domain.theme import Theme
from github_profiler.infrastructure.cache import LocalFSCache
from github_profiler.infrastructure.dashboard_renderer import DashboardRenderer
from github_profiler.infrastructure.plugin_loader import FilesystemPluginLoader
from github_profiler.infrastructure.rendering import SVGEngine


def _generate_test_image() -> bytes:
    img = Image.new("RGB", (100, 100), color="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@patch("github_profiler.application.plugins.ascii_portrait.requests.get")
@patch("github_profiler.application.plugins.ascii_portrait.remove")
def test_ascii_portrait_unit(mock_remove, mock_get) -> None:  # type: ignore
    """Unit test for ASCII Portrait generation logic."""
    mock_get.return_value.content = _generate_test_image()
    mock_get.return_value.raise_for_status.return_value = None
    mock_remove.return_value = _generate_test_image()

    plugin = AsciiPortraitPlugin(width=20, remove_bg=True)
    user = GitHubUser(
        username="test",
        name=None,
        bio=None,
        company=None,
        location=None,
        avatar_url="http://test.com/img.png",
        followers=0,
        following=0,
    )
    theme = Theme()

    comp = plugin.generate(user, theme)
    assert isinstance(comp, Canvas)
    # 1 bg + lines
    assert len(comp.children) > 1


def test_ascii_portrait_snapshot() -> None:
    """Snapshot test verifying exact structural output on fallback."""
    plugin = AsciiPortraitPlugin(width=10, remove_bg=False)
    user = GitHubUser(
        username="test",
        name=None,
        bio=None,
        company=None,
        location=None,
        avatar_url="",
        followers=0,
        following=0,
    )
    theme = Theme()
    comp = plugin.generate(user, theme)

    assert isinstance(comp, Canvas)
    assert getattr(comp.children[1], "content") == "No Avatar"


def test_ascii_portrait_benchmark() -> None:
    """Performance benchmark for ASCII generation without network."""
    plugin = AsciiPortraitPlugin(width=20, remove_bg=False)
    user = GitHubUser(
        username="test",
        name=None,
        bio=None,
        company=None,
        location=None,
        avatar_url="",
        followers=0,
        following=0,
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
        )


def test_ascii_portrait_integration(tmp_path: Path) -> None:
    """Integration test end-to-end with DashboardOrchestrator."""
    config_file = tmp_path / "profile.toml"
    config_file.write_text('plugins = ["ascii_portrait"]')

    config_mgr = ConfigManager(config_file)
    plugin_mgr = PluginManager(FilesystemPluginLoader())
    gen_service = DashboardGenerationService(
        MockGitHubClient(), LocalFSCache(tmp_path), DashboardRenderer()
    )
    orchestrator = DashboardOrchestrator(config_mgr, plugin_mgr, gen_service, EventBus())

    svg = orchestrator.build_profile("integrator")
    assert "No Avatar" in svg


def test_ascii_portrait_migration() -> None:
    """Verifies V2 -> V3 migration perfectly preserves visual output and layout constraints."""
    plugin = AsciiPortraitPlugin(width=10, remove_bg=False)
    user = GitHubUser(
        username="test", name=None, bio=None, company=None,
        location=None, avatar_url="", followers=0, following=0
    )
    theme = Theme()

    # 1. Generate new V3 Canvas
    canvas = plugin.generate(user, theme)
    assert isinstance(canvas, Canvas)
    size = canvas.measure()
    assert size.width > 0
    assert size.height > 0

    # 2. Legacy Engine SVG
    legacy_group = ComponentGroup(x=canvas.x, y=canvas.y)
    legacy_group.children = canvas.children
    legacy_engine = SVGEngine()
    legacy_svg = legacy_engine.render([legacy_group], theme)

    # 3. Dashboard Engine SVG
    dash = Dashboard(children=[canvas], gap=0)
    dash.padding = Padding.all(0)
    dashboard_engine = DashboardRenderer()
    dashboard_svg = dashboard_engine.render(dash, theme)

    # Compare
    ns = {"svg": "http://www.w3.org/2000/svg"}
    legacy_root = ET.fromstring(legacy_svg)
    dash_root = ET.fromstring(dashboard_svg)

    legacy_texts = legacy_root.findall(".//svg:text", ns)
    dash_texts = dash_root.findall(".//svg:text", ns)

    assert len(legacy_texts) == len(dash_texts)
    for lt, dt in zip(legacy_texts, dash_texts):
        assert lt.attrib["x"] == dt.attrib["x"]
        assert lt.attrib["y"] == dt.attrib["y"]
        assert lt.text == dt.text

    legacy_rects = legacy_root.findall(".//svg:rect", ns)
    dash_rects = dash_root.findall(".//svg:rect", ns)

    legacy_plugin_rects = [r for r in legacy_rects if "rx" in r.attrib]
    dash_plugin_rects = [r for r in dash_rects if "rx" in r.attrib]

    assert len(legacy_plugin_rects) == len(dash_plugin_rects)
    for lr, dr in zip(legacy_plugin_rects, dash_plugin_rects):
        assert lr.attrib["width"] == dr.attrib["width"]
        assert lr.attrib["height"] == dr.attrib["height"]
        assert lr.attrib["rx"] == dr.attrib["rx"]
