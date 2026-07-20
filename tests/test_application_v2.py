from pathlib import Path

from github_profiler.application.event_bus import EventBus
from github_profiler.domain.events import Event
from github_profiler.application.config_manager import ConfigManager


def test_event_bus() -> None:
    bus = EventBus()
    received = []

    def callback(event: Event) -> None:
        received.append(event.payload)

    bus.subscribe("test_event", callback)
    bus.publish(Event(name="test_event", payload={"data": 1}))
    bus.publish(Event(name="other_event", payload={"data": 2}))

    assert len(received) == 1
    assert received[0] == {"data": 1}


def test_config_manager(tmp_path: Path) -> None:
    config_file = tmp_path / "profile.toml"
    config_file.write_text('plugins = ["test_plugin"]')

    mgr = ConfigManager(config_file)
    plugins = mgr.get_plugins()
    assert plugins == ["test_plugin"]
