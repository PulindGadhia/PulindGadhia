import datetime
import time
from pathlib import Path

from github_profiler.application.config_manager import ConfigManager
from github_profiler.application.event_bus import EventBus
from github_profiler.application.orchestrator import (
    GenerationService,
    ProfileOrchestrator,
)
from github_profiler.application.plugin_manager import PluginManager
from github_profiler.application.plugins.heatmap import HeatmapPlugin
from github_profiler.domain.components import ComponentBox, ComponentGroup
from github_profiler.domain.interfaces import IGitHubClient
from github_profiler.domain.models import ContributionDay, GitHubUser, ProfileStats
from github_profiler.domain.theme import Theme
from github_profiler.infrastructure.cache import LocalFSCache
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
    """Unit test for Heatmap generation logic."""
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
    )
    theme = Theme()

    comp = plugin.generate(user, theme)
    assert isinstance(comp, ComponentGroup)
    # 1 background box + 10 cell boxes
    assert len(comp.children) == 11

    bg = comp.children[0]
    assert isinstance(bg, ComponentBox)
    assert getattr(bg, "width") > 0

    first_cell = comp.children[1]
    assert isinstance(first_cell, ComponentBox)
    # The first cell should have 0 count, so it uses theme secondary color
    assert getattr(first_cell, "fill_color") == theme.palette.secondary
    assert getattr(first_cell, "attributes")["title"] == "0 contributions on 2023-01-01"


def test_heatmap_snapshot() -> None:
    """Snapshot test verifying layout coordinates and spacing."""
    plugin = HeatmapPlugin()
    calendar = _generate_mock_calendar(8)  # 1 full week + 1 day
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
    )
    theme = Theme()
    comp = plugin.generate(user, theme)

    assert isinstance(comp, ComponentGroup)
    # Week 1, Day 1
    cell1 = comp.children[1]
    # Week 2, Day 1
    cell8 = comp.children[8]

    assert getattr(cell1, "x") == 4
    assert getattr(cell1, "y") == 4

    # Week 2 should be shifted right by CELL_SIZE (10) + CELL_GAP (4) = 14
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
    )
    theme = Theme()

    start = time.perf_counter()
    for _ in range(100):
        plugin.generate(user, theme)
    duration = time.perf_counter() - start
    # 100 generations of 365 cells should be extremely fast (<< 0.5s)
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


def test_heatmap_integration(tmp_path: Path) -> None:
    """Integration test end-to-end with Orchestrator."""
    config_file = tmp_path / "profile.toml"
    config_file.write_text('plugins = ["heatmap"]')

    config_mgr = ConfigManager(config_file)
    plugin_mgr = PluginManager(FilesystemPluginLoader())
    gen_service = GenerationService(
        MockGitHubClient(), LocalFSCache(tmp_path), SVGEngine()
    )
    orchestrator = ProfileOrchestrator(config_mgr, plugin_mgr, gen_service, EventBus())

    svg = orchestrator.build_profile("integrator")
    assert "data-tooltip" in svg
