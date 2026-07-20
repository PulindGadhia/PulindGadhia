import time
from pathlib import Path

from github_profiler.application.config_manager import ConfigManager
from github_profiler.application.event_bus import EventBus
from github_profiler.application.orchestrator import (
    GenerationService,
    ProfileOrchestrator,
)
from github_profiler.application.plugin_manager import PluginManager
from github_profiler.application.plugins.neofetch import NeofetchPlugin
from github_profiler.domain.components import ComponentGroup, ComponentText
from github_profiler.domain.interfaces import IGitHubClient
from github_profiler.domain.models import GitHubUser, ProfileStats
from github_profiler.domain.theme import Theme
from github_profiler.infrastructure.cache import LocalFSCache
from github_profiler.infrastructure.plugin_loader import FilesystemPluginLoader
from github_profiler.infrastructure.rendering import SVGEngine


def test_neofetch_unit() -> None:
    """Unit test for Neofetch generation logic."""
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

    component = plugin.generate(user, theme)
    assert isinstance(component, ComponentGroup)
    assert len(component.children) == 8  # 1 bg + 7 lines

    text_comp = component.children[1]
    assert isinstance(text_comp, ComponentText)
    assert text_comp.content == "octocat@github"


def test_neofetch_snapshot() -> None:
    """Snapshot test verifying exact structural output."""
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
    component = plugin.generate(user, theme)

    assert isinstance(component, ComponentGroup)
    lines = [
        child.content
        for child in component.children
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
    """Performance benchmark for Neofetch generation."""
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

    # Must generate 1000 neofetches in under 500ms
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


def test_neofetch_integration(tmp_path: Path) -> None:
    """Integration test end-to-end with Orchestrator."""
    config_file = tmp_path / "profile.toml"
    config_file.write_text('plugins = ["neofetch"]')

    config_mgr = ConfigManager(config_file)
    plugin_mgr = PluginManager(FilesystemPluginLoader())
    gen_service = GenerationService(
        MockGitHubClient(), LocalFSCache(tmp_path), SVGEngine()
    )
    orchestrator = ProfileOrchestrator(config_mgr, plugin_mgr, gen_service, EventBus())

    svg = orchestrator.build_profile("integrator")
    assert "integrator@github" in svg
