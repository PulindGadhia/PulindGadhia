"""V3 Dashboard Layout Engine.

Calculates the absolute layout positions for Dashboard semantic containers
without mutating the original tree (Pure Function).
"""

from dataclasses import replace
from typing import Any, Dict, Type

from github_profiler.domain.components import (
    Canvas,
    Card,
    Column,
    Dashboard,
    Row,
    UIComponent,
)


class ILayoutStrategy:
    """Strategy interface for layout computation."""

    def layout(
        self, node: Any, x: float, y: float, engine: "DashboardLayoutEngine"
    ) -> UIComponent:
        """Applies layout logic to position children of the node."""
        raise NotImplementedError


class CanvasStrategy(ILayoutStrategy):
    """Layout strategy for Canvases (The Black Box Rule)."""

    def layout(
        self, node: Canvas, x: float, y: float, engine: "DashboardLayoutEngine"
    ) -> UIComponent:
        # We assign x and y to the Canvas itself, but we absolutely
        # DO NOT iterate over its children. They remain perfectly isolated.
        return replace(node, x=x, y=y)


class CardStrategy(ILayoutStrategy):
    """Layout strategy for Cards."""

    def layout(
        self, node: Card, x: float, y: float, engine: "DashboardLayoutEngine"
    ) -> UIComponent:
        # Calculate where the content sits absolutely
        content_x = x + node.padding.left + node.margin.left
        content_y = y + node.padding.top + node.margin.top

        new_content = engine.layout(node.content, content_x, content_y)
        return replace(node, x=x, y=y, content=new_content)


class RowStrategy(ILayoutStrategy):
    """Layout strategy for horizontal rows."""

    def layout(
        self, node: Row, x: float, y: float, engine: "DashboardLayoutEngine"
    ) -> UIComponent:
        new_children = []
        curr_x = x + node.padding.left
        curr_y = y + node.padding.top

        for i, child in enumerate(node.children):
            if i > 0:
                curr_x += node.gap

            # Simplified alignment mapping
            if node.align_items == "center":
                child_y = curr_y + (node.height - child.height) / 2
            else:
                child_y = curr_y

            new_child = engine.layout(child, curr_x, child_y)
            new_children.append(new_child)
            curr_x += new_child.width

        return replace(node, x=x, y=y, children=new_children)


class ColumnStrategy(ILayoutStrategy):
    """Layout strategy for vertical columns."""

    def layout(
        self, node: Column, x: float, y: float, engine: "DashboardLayoutEngine"
    ) -> UIComponent:
        new_children = []
        curr_x = x + node.padding.left
        curr_y = y + node.padding.top

        for i, child in enumerate(node.children):
            if i > 0:
                curr_y += node.gap

            if node.justify_content == "center":
                child_x = curr_x + (node.width - child.width) / 2
            else:
                child_x = curr_x

            new_child = engine.layout(child, child_x, curr_y)
            new_children.append(new_child)
            curr_y += new_child.height

        return replace(node, x=x, y=y, children=new_children)


class DashboardStrategy(ILayoutStrategy):
    """Layout strategy for the root Dashboard."""

    def layout(
        self, node: Dashboard, x: float, y: float, engine: "DashboardLayoutEngine"
    ) -> UIComponent:
        # The Dashboard behaves like a Column
        new_children = []
        curr_x = x + node.padding.left
        curr_y = y + node.padding.top

        for i, child in enumerate(node.children):
            if i > 0:
                curr_y += node.gap

            new_child = engine.layout(child, curr_x, curr_y)
            new_children.append(new_child)
            curr_y += new_child.height

        return replace(node, x=x, y=y, children=new_children)


class DefaultStrategy(ILayoutStrategy):
    """Fallback strategy for unsupported or legacy components."""

    def layout(
        self, node: UIComponent, x: float, y: float, engine: "DashboardLayoutEngine"
    ) -> UIComponent:
        return replace(node, x=x, y=y)


class DashboardLayoutEngine:
    """A pure-function layout engine for V3 Dashboard elements."""

    def __init__(self) -> None:
        self.strategies: Dict[Type[UIComponent], ILayoutStrategy] = {
            Canvas: CanvasStrategy(),
            Card: CardStrategy(),
            Row: RowStrategy(),
            Column: ColumnStrategy(),
            Dashboard: DashboardStrategy(),
        }
        self.default_strategy = DefaultStrategy()

    def layout(self, node: UIComponent, x: float = 0.0, y: float = 0.0) -> UIComponent:
        """Positions the node and its children returning a new immutable tree."""
        strategy = self.strategies.get(type(node), self.default_strategy)
        return strategy.layout(node, x, y, self)
