"""V3 Dashboard Renderer.

Coordinates the pipeline: Measurement -> Layout -> SVG Builder.
"""

from typing import Any, Dict

from github_profiler.domain.components import (
    Canvas,
    Card,
    Column,
    ComponentBox,
    ComponentGroup,
    ComponentText,
    Dashboard,
    Row,
    UIComponent,
)
from github_profiler.domain.theme import Theme
from github_profiler.domain.interfaces import IDashboardRenderer
from github_profiler.infrastructure.dashboard_layout import DashboardLayoutEngine
from github_profiler.infrastructure.svg_builder import SVGBuilder


class DashboardRenderer(IDashboardRenderer):
    """The rendering facade orchestrating layout and builder patterns."""

    def __init__(self) -> None:
        self.layout_engine = DashboardLayoutEngine()

    def render(self, dashboard: Dashboard, theme: Theme) -> str:
        """Executes the rendering pipeline."""
        # Pass 1: Measure
        dashboard.measure()

        # Pass 2: Layout
        positioned_tree = self.layout_engine.layout(dashboard)

        # Pass 3: Render Traversal
        builder = SVGBuilder(
            width=positioned_tree.width,
            height=positioned_tree.height,
            bg_color=theme.palette.background,
        )

        builder.add_drop_shadow("card-shadow")

        # Global typography wrapping
        builder.begin_group(font_family=theme.typography.font_stack)
        self._traverse(positioned_tree, builder, theme)
        builder.end_group()

        return builder.build()

    def _traverse(self, node: UIComponent, builder: SVGBuilder, theme: Theme) -> None:
        """Pure traversal logic routing nodes to SVG primitive calls."""

        if isinstance(node, (Dashboard, Row, Column)):
            # Structural layout elements emit zero SVG themselves
            for child in getattr(node, "children", []):
                self._traverse(child, builder, theme)

        elif isinstance(node, Card):
            # The Card acts as the stylized visual boundary
            filter_attr = "url(#card-shadow)" if node.shadow else None
            bg = node.bg_color or theme.palette.background

            builder.add_rect(
                x=node.x,
                y=node.y,
                width=node.width,
                height=node.height,
                rx=node.border_radius,
                fill=bg,
                stroke=theme.window.border_color,
                filter=filter_attr,
            )

            # Descend into the inner plugin Canvas
            if hasattr(node, "content"):
                self._traverse(node.content, builder, theme)

        elif isinstance(node, Canvas):
            # The Black Box Translation
            # Internal coordinates remain relative to 0,0 since we translate the <g>
            builder.begin_group(transform=f"translate({node.x}, {node.y})")

            for child in getattr(node, "children", []):
                self._traverse_plugin_node(child, builder, theme)

            builder.end_group()

    def _traverse_plugin_node(
        self, node: UIComponent, builder: SVGBuilder, theme: Theme
    ) -> None:
        """Renders legacy inner plugin components inside the translated Canvas."""
        attrs: Dict[str, Any] = (
            node.attributes.copy() if hasattr(node, "attributes") else {}
        )

        if isinstance(node, ComponentBox):
            rx = getattr(node, "border_radius", 0)
            fill = getattr(node, "fill_color", "none")
            stroke = getattr(node, "stroke_color", None)

            if stroke:
                attrs["stroke"] = stroke

            stroke_width = getattr(node, "stroke_width", 0)
            if stroke_width > 0:
                attrs["stroke-width"] = stroke_width

            builder.add_rect(
                node.x, node.y, node.width, node.height, rx=rx, fill=fill, **attrs
            )

        elif isinstance(node, ComponentText):
            color = getattr(node, "color", theme.palette.foreground)
            font_size = getattr(node, "font_size", theme.typography.text_size)
            anchor = getattr(node, "text_anchor", "start")

            # Properly map hyphenated SVG properties
            attrs["dominant-baseline"] = "hanging"
            attrs["font-size"] = font_size
            attrs["text-anchor"] = anchor

            builder.add_text(
                content=node.content, x=node.x, y=node.y, fill=color, **attrs
            )

        elif isinstance(node, ComponentGroup):
            # V2 nested groups
            builder.begin_group(**attrs)
            for child in getattr(node, "children", []):
                self._traverse_plugin_node(child, builder, theme)
            builder.end_group()
