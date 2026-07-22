"""Command Line Interface for GitHub Profiler."""

import argparse
import logging
from pathlib import Path
from typing import List, Optional

from github_profiler.application.config_manager import ConfigManager
from github_profiler.application.event_bus import EventBus
from github_profiler.application.dashboard_orchestrator import (
    DashboardGenerationService,
    DashboardOrchestrator,
)
from github_profiler.application.orchestrator import (
    GenerationService,
    ProfileOrchestrator,
)
from github_profiler.application.plugin_manager import PluginManager
from github_profiler.domain.events import Event
from github_profiler.infrastructure.cache import LocalFSCache
from github_profiler.infrastructure.graphql_client import GitHubGraphQLClient
from github_profiler.infrastructure.plugin_loader import FilesystemPluginLoader
from github_profiler.infrastructure.rendering import SVGEngine
from github_profiler.infrastructure.dashboard_renderer import DashboardRenderer

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run_cli(args: Optional[List[str]] = None) -> int:
    """Parses arguments and runs the generation pipeline."""
    parser = argparse.ArgumentParser(description="GitHub Profiler v2.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate", help="Generate profile SVG")
    gen_parser.add_argument(
        "--config", type=str, required=True, help="Path to profile.toml"
    )
    gen_parser.add_argument(
        "--username", type=str, required=True, help="GitHub username"
    )
    gen_parser.add_argument(
        "--out", type=str, default="profile.svg", help="Output file"
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.command == "generate":
        try:
            # 1. Dependency Injection Wiring
            config_path = Path(parsed_args.config)
            cache_dir = Path(".cache")

            # Infrastructure
            github_client = GitHubGraphQLClient()
            cache = LocalFSCache(cache_dir)
            renderer = DashboardRenderer()
            plugin_loader = FilesystemPluginLoader()

            # Application
            event_bus = EventBus()
            config_mgr = ConfigManager(config_path)
            plugin_mgr = PluginManager(plugin_loader)
            gen_service = DashboardGenerationService(github_client, cache, renderer)

            orchestrator = DashboardOrchestrator(
                config_mgr, plugin_mgr, gen_service, event_bus
            )

            # Progress reporting via EventBus
            def on_pre_fetch(event: Event) -> None:
                logger.info(f"Fetching data for user: {event.payload.get('username')}")

            def on_post_fetch(event: Event) -> None:
                logger.info("Data fetched successfully.")

            def on_pre_render(event: Event) -> None:
                logger.info("Rendering SVG components...")

            event_bus.subscribe("pre_fetch", on_pre_fetch)
            event_bus.subscribe("post_fetch", on_post_fetch)
            event_bus.subscribe("pre_render", on_pre_render)

            # 2. Execute
            logger.info("Starting generation pipeline...")
            svg_string = orchestrator.build_profile(parsed_args.username)

            # 3. Export
            out_path = Path(parsed_args.out)
            out_path.write_text(svg_string)
            logger.info(f"Success! Profile written to {out_path}")

            return 0
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return 1

    return 1
