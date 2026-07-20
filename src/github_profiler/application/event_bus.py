"""Event Bus implementation for lifecycle hooks."""

from typing import Callable, Dict, List

from github_profiler.domain.events import Event
from github_profiler.domain.interfaces import IEventBus


class EventBus(IEventBus):
    """Publish-subscribe event bus."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, event_name: str, callback: Callable[[Event], None]) -> None:
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def publish(self, event: Event) -> None:
        if event.name in self._subscribers:
            for callback in self._subscribers[event.name]:
                callback(event)
