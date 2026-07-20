import io
import time
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from github_profiler.application.config_manager import ConfigManager
from github_profiler.application.event_bus import EventBus
from github_profiler.application.orchestrator import (
    GenerationService,
    ProfileOrchestrator,
)
from github_profiler.application.plugin_manager import PluginManager
from github_profiler.application.plugins.ascii_portrait import AsciiPortraitPlugin
from github_profiler.domain.components import ComponentGroup
from github_profiler.domain.interfaces import IGitHubClient
from github_profiler.domain.models import GitHubUser, ProfileStats
from github_profiler.domain.theme import Theme
from github_profiler.infrastructure.cache import LocalFSCache
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
    assert isinstance(comp, ComponentGroup)
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

    assert isinstance(comp, ComponentGroup)
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
    """Integration test end-to-end with Orchestrator."""
    config_file = tmp_path / "profile.toml"
    config_file.write_text('plugins = ["ascii_portrait"]')

    config_mgr = ConfigManager(config_file)
    plugin_mgr = PluginManager(FilesystemPluginLoader())
    gen_service = GenerationService(
        MockGitHubClient(), LocalFSCache(tmp_path), SVGEngine()
    )
    orchestrator = ProfileOrchestrator(config_mgr, plugin_mgr, gen_service, EventBus())

    svg = orchestrator.build_profile("integrator")
    assert "No Avatar" in svg
