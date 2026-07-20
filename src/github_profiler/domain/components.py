"""Abstract UI Component models.

These classes provide a purely logical representation of the UI layout,
completely decoupled from the actual rendering implementation (e.g., SVG or HTML).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(slots=True)
class UIComponent:
    """Base class for all UI components."""

    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    attributes: Dict[str, str] = field(default_factory=dict)
    animation_type: Optional[str] = None
    animation_delay_ms: int = 0


@dataclass(slots=True)
class ComponentBox(UIComponent):
    """A rectangular layout box."""

    border_radius: float = 0.0
    fill_color: str = "transparent"
    stroke_color: Optional[str] = None
    stroke_width: int = 0


@dataclass(slots=True)
class ComponentText(UIComponent):
    """A textual element."""

    content: str = ""
    font_size: int = 14
    font_weight: str = "normal"
    color: str = "#ffffff"
    text_anchor: str = "start"


@dataclass(slots=True)
class ComponentGroup(UIComponent):
    """A logical grouping of multiple components."""

    children: List[UIComponent] = field(default_factory=list)
