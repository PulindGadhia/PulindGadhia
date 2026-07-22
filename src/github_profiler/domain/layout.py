"""Layout primitives for GitHub Profiler."""

from dataclasses import dataclass, field
from typing import List, Optional

from github_profiler.domain.components import UIComponent


@dataclass
class LayoutItem:
    """A UI component placed inside a layout."""

    component: UIComponent
    width: Optional[int] = None
    height: Optional[int] = None
    flex: int = 1


@dataclass
class Row:
    """Horizontal container."""

    children: List[LayoutItem] = field(default_factory=list)
    spacing: int = 20
    padding: int = 20


@dataclass
class Column:
    """Vertical container."""

    children: List[LayoutItem] = field(default_factory=list)
    spacing: int = 20
    padding: int = 20


@dataclass
class Grid:
    """Grid container."""

    columns: int
    spacing: int = 20
    children: List[LayoutItem] = field(default_factory=list)


@dataclass
class Dashboard:
    """Root dashboard layout."""

    children: List[object] = field(default_factory=list)
    padding: int = 30
    spacing: int = 30