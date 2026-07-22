import xml.etree.ElementTree as ET
from pathlib import Path

from github_profiler.application.config_manager import ConfigManager
from github_profiler.application.dashboard_orchestrator import (
    DashboardGenerationService,
    DashboardOrchestrator,
)
from github_profiler.application.event_bus import EventBus
from github_profiler.application.plugin_manager import PluginManager
from github_profiler.domain.interfaces import IGitHubClient
from github_profiler.domain.models import ContributionDay, GitHubUser, ProfileStats
from github_profiler.infrastructure.cache import LocalFSCache
from github_profiler.infrastructure.dashboard_renderer import DashboardRenderer
from github_profiler.infrastructure.plugin_loader import FilesystemPluginLoader


import datetime

class MockGitHubClient(IGitHubClient):
    def fetch_user_data(self, username: str) -> GitHubUser:
        stats = ProfileStats(total_repositories=12)
        return GitHubUser(
            username=username,
            name="Test User",
            bio=None,
            company=None,
            location=None,
            followers=100,
            following=50,
            stats=stats,
            avatar_url="",
            contribution_calendar=[ContributionDay(date=datetime.date(2023, 1, 1), contribution_count=5, color="#00ff00")],
        )


def test_complete_dashboard_generation(tmp_path: Path) -> None:
    """Phase 6E: Generates a complete dashboard containing ASCII, Neofetch, and Heatmap."""
    config_file = tmp_path / "profile.toml"
    # DashboardOrchestrator inherently loads all 3 when generating the flex layout, 
    # but we list them here to ensure the PluginManager loads them.
    config_file.write_text('plugins = ["ascii_portrait", "neofetch", "heatmap"]')

    config_mgr = ConfigManager(config_file)
    plugin_mgr = PluginManager(FilesystemPluginLoader())
    gen_service = DashboardGenerationService(
        MockGitHubClient(), LocalFSCache(tmp_path), DashboardRenderer()
    )
    orchestrator = DashboardOrchestrator(
        config_mgr, plugin_mgr, gen_service, EventBus()
    )

    svg = orchestrator.build_profile("integrator")
    
    # Verify valid SVG
    assert svg.startswith('<svg')
    root = ET.fromstring(svg)
    ns = {"svg": "http://www.w3.org/2000/svg"}
    
    # 1. Correct Layout (Check groups with translations)
    groups = root.findall(".//svg:g", ns)
    
    # We expect translation groups for Row, Column, Cards, and Canvases.
    # ASCII Portrait should output "No Avatar"
    # Neofetch should output "integrator@github"
    # Heatmap should output data-tooltip
    assert "No Avatar" in svg
    assert "integrator@github" in svg
    assert "data-tooltip" in svg

    # 2. Verify no overlap (cards translated away from each other)
    translations = [g.attrib.get("transform") for g in groups if "transform" in g.attrib]
    assert len(translations) > 0
    # Make sure we have different translation coordinates (implying non-overlapping layout engine logic)
    unique_translations = set(translations)
    assert len(unique_translations) > 1

    # 3. Correct measurements (width and height of SVG should encompass all plugins)
    width = float(root.attrib["width"])
    height = float(root.attrib["height"])
    assert width > 500  # Neofetch + ASCII + gaps
    assert height > 200 # Height should cover the tallest components

