from pathlib import Path

from github_profiler.infrastructure.cache import LocalFSCache
from github_profiler.infrastructure.plugin_loader import FilesystemPluginLoader
from github_profiler.infrastructure.rendering import SVGEngine
from github_profiler.domain.components import ComponentBox, ComponentText
from github_profiler.domain.theme import Theme


def test_local_fs_cache(tmp_path: Path) -> None:
    cache = LocalFSCache(tmp_path)
    cache.set("test_key", {"data": 123})
    assert cache.get("test_key") == {"data": 123}
    assert cache.get("missing") is None


def test_svg_engine() -> None:
    engine = SVGEngine()
    components = [
        ComponentBox(width=100, height=50, fill_color="red"),
        ComponentText(content="Hello", animation_type="typewriter"),
    ]
    theme = Theme()
    svg = engine.render(components, theme)
    assert 'width="100"' in svg
    assert "Hello" in svg
    assert "@keyframes typing" in svg


def test_plugin_loader() -> None:
    loader = FilesystemPluginLoader()
    plugins = loader.load_plugins(["nonexistent_plugin"])
    assert len(plugins) == 0
