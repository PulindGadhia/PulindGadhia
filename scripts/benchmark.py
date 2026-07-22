import time
import tracemalloc
from pathlib import Path

from github_profiler.application.config_manager import ConfigManager
from github_profiler.application.dashboard_orchestrator import (
    DashboardGenerationService,
    DashboardOrchestrator,
)
from github_profiler.application.event_bus import EventBus
from github_profiler.application.plugin_manager import PluginManager
from github_profiler.domain.interfaces import IGitHubClient
from github_profiler.domain.models import GitHubUser, ProfileStats
from github_profiler.infrastructure.cache import LocalFSCache
from github_profiler.infrastructure.dashboard_renderer import DashboardRenderer
from github_profiler.infrastructure.plugin_loader import FilesystemPluginLoader

class MockGitHubClient(IGitHubClient):
    def fetch_user_data(self, username: str) -> GitHubUser:
        stats = ProfileStats(total_repositories=12)
        return GitHubUser(
            username=username,
            name="Benchmark User",
            bio=None,
            company=None,
            location=None,
            followers=100,
            following=50,
            stats=stats,
            avatar_url="",
        )

def run_benchmark(num_plugins: int) -> None:
    available = ["ascii_portrait", "neofetch", "heatmap"]
    plugins_to_load = [available[i % len(available)] for i in range(num_plugins)]
    
    config_file = Path("benchmark_profile.toml")
    config_content = 'plugins = [\n' + ',\n'.join(f'"{p}"' for p in plugins_to_load) + '\n]'
    config_file.write_text(config_content)
    
    # Measure cold start
    tracemalloc.start()
    start_time = time.perf_counter()
    
    config_mgr = ConfigManager(config_file)
    plugin_mgr = PluginManager(FilesystemPluginLoader())
    gen_service = DashboardGenerationService(
        MockGitHubClient(), LocalFSCache(Path(".cache")), DashboardRenderer()
    )
    orchestrator = DashboardOrchestrator(
        config_mgr, plugin_mgr, gen_service, EventBus()
    )
    
    svg = orchestrator.build_profile("benchmark")
    
    cold_time = time.perf_counter() - start_time
    _, peak_mem_cold = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Measure warm start
    tracemalloc.start()
    start_time = time.perf_counter()
    svg = orchestrator.build_profile("benchmark")
    warm_time = time.perf_counter() - start_time
    _, peak_mem_warm = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    svg_size = len(svg.encode("utf-8"))
    
    print(f"| {num_plugins} | {cold_time*1000:.2f}ms | {warm_time*1000:.2f}ms | {peak_mem_cold/1024:.2f}KB | {peak_mem_warm/1024:.2f}KB | {svg_size/1024:.2f}KB |")
    config_file.unlink()

if __name__ == "__main__":
    print("| Plugins | Cold CPU | Warm CPU | Cold Mem | Warm Mem | SVG Size |")
    print("|---------|----------|----------|----------|----------|----------|")
    for count in [1, 3, 10, 25, 100]:
        run_benchmark(count)
