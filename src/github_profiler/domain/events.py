"""Domain events and event bus types."""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(slots=True)
class Event:
    """A standard event payload emitted via the Event Bus."""

    name: str
    payload: Dict[str, Any]
