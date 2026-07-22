"""Abstract UI Component models.

These classes provide a purely logical representation of the UI layout,
completely decoupled from the actual rendering implementation (e.g., SVG or HTML).
"""

import warnings
from dataclasses import dataclass, field
from typing import ClassVar, Dict, List, Optional

from github_profiler.domain.geometry import Margin, Padding, Size


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

    def measure(self) -> Size:
        """Returns the geometric footprint of this component."""
        return Size(width=self.width, height=self.height)


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

    _warned: ClassVar[bool] = False

    def __post_init__(self) -> None:
        if not ComponentGroup._warned:
            warnings.warn("ComponentGroup is deprecated and will be removed in v3.1.", DeprecationWarning, stacklevel=2)
            ComponentGroup._warned = True

    # Layout properties
    direction: str = "vertical"  # vertical | horizontal | absolute
    gap: int = 10
    padding: int = 0
    align: str = "start"  # start | center | end

    def measure(self) -> Size:
        # V2 fallback measurement
        max_w = self.width
        max_h = self.height
        for child in self.children:
            sz = child.measure()
            if self.direction == "vertical":
                max_h += sz.height + self.gap
                max_w = max(max_w, sz.width)
            else:
                pass  # V2 only properly did vertical
        return Size(width=max_w, height=max_h)


# ---------------------------------------------------------
# V3 Architecture Domain Models
# ---------------------------------------------------------


@dataclass(slots=True)
class Canvas(UIComponent):
    """An isolated absolute coordinate space for plugins (The Black Box).
    The LayoutEngine is forbidden from modifying the x/y of its children.
    """

    children: List[UIComponent] = field(default_factory=list)

    def measure(self) -> Size:
        """Measures the bounding box of all absolute children if width/height not set."""
        if self.width > 0 and self.height > 0:
            return Size(width=self.width, height=self.height)

        max_w = 0.0
        max_h = 0.0
        for child in self.children:
            child_size = child.measure()
            if child.x + child_size.width > max_w:
                max_w = child.x + child_size.width
            if child.y + child_size.height > max_h:
                max_h = child.y + child_size.height

        self.width = max_w
        self.height = max_h
        return Size(width=max_w, height=max_h)


@dataclass(slots=True)
class Card(UIComponent):
    """A visual wrapper boundary providing padding, margins, shadows, and backgrounds.
    It encapsulates exactly one child (usually a Canvas) to isolate plugin logic from dashboard layouts.
    """

    content: UIComponent = field(default_factory=UIComponent)
    padding: Padding = field(default_factory=lambda: Padding.all(15.0))
    margin: Margin = field(default_factory=lambda: Margin.all(10.0))
    shadow: bool = True
    bg_color: Optional[str] = None
    border_radius: int = 8

    def measure(self) -> Size:
        """Measures the content plus padding and margin."""
        content_size = self.content.measure()

        w = (
            content_size.width
            + self.padding.left
            + self.padding.right
            + self.margin.left
            + self.margin.right
        )
        h = (
            content_size.height
            + self.padding.top
            + self.padding.bottom
            + self.margin.top
            + self.margin.bottom
        )

        self.width = w
        self.height = h
        return Size(width=w, height=h)


@dataclass(slots=True)
class LayoutNode(UIComponent):
    """Base class for V3 flex layouts."""

    children: List[UIComponent] = field(default_factory=list)
    gap: float = 10.0
    padding: Padding = field(default_factory=Padding)


@dataclass(slots=True)
class Row(LayoutNode):
    """A horizontal flex layout container."""

    align_items: str = "start"

    def measure(self) -> Size:
        """Measures all children horizontally."""
        w = self.padding.left + self.padding.right
        h = 0.0

        for i, child in enumerate(self.children):
            sz = child.measure()
            w += sz.width
            if i > 0:
                w += self.gap
            if sz.height > h:
                h = sz.height

        h += self.padding.top + self.padding.bottom
        self.width = w
        self.height = h
        return Size(width=w, height=h)


@dataclass(slots=True)
class Column(LayoutNode):
    """A vertical flex layout container."""

    justify_content: str = "start"

    def measure(self) -> Size:
        """Measures all children vertically."""
        w = 0.0
        h = self.padding.top + self.padding.bottom

        for i, child in enumerate(self.children):
            sz = child.measure()
            h += sz.height
            if i > 0:
                h += self.gap
            if sz.width > w:
                w = sz.width

        w += self.padding.left + self.padding.right
        self.width = w
        self.height = h
        return Size(width=w, height=h)


@dataclass(slots=True)
class Dashboard(LayoutNode):
    """The root V3 layout document."""

    theme_name: str = "dark"

    def measure(self) -> Size:
        """Dashboard layout operates exactly like a Column layout."""
        w = 0.0
        h = self.padding.top + self.padding.bottom

        for i, child in enumerate(self.children):
            sz = child.measure()
            h += sz.height
            if i > 0:
                h += self.gap
            if sz.width > w:
                w = sz.width

        w += self.padding.left + self.padding.right
        self.width = w
        self.height = h
        return Size(width=w, height=h)
