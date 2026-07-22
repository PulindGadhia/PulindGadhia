"""SVG Builder for constructing XML documents programmatically.

This module acts as a pure rendering backend with zero knowledge of UI layouts,
plugins, or dashboards. It strictly handles SVG syntax generation.
"""

import html
from typing import Any, Dict, List


class SVGBuilder:
    """A rendering backend that constructs SVG documents using the Builder pattern."""

    def __init__(self, width: float, height: float, bg_color: str = "#0d1117") -> None:
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.defs: List[str] = []
        self.elements: List[str] = []
        self._indent_level = 1

    def _indent(self) -> str:
        return "  " * self._indent_level

    def _format_attrs(self, attrs: Dict[str, Any]) -> str:
        if not attrs:
            return ""

        formatted = []
        for k, v in attrs.items():
            if v is not None:
                formatted.append(f'{k}="{html.escape(str(v))}"')
        return " " + " ".join(formatted) if formatted else ""

    def add_filter(self, filter_id: str, content: str) -> "SVGBuilder":
        """Adds a raw filter definition to <defs>."""
        self.defs.append(f'<filter id="{filter_id}">\n{content}\n</filter>')
        return self

    def add_drop_shadow(self, shadow_id: str = "shadow") -> "SVGBuilder":
        """Adds a standard drop shadow filter."""
        shadow = (
            '  <feDropShadow dx="0" dy="4" stdDeviation="4" '
            'flood-color="#000000" flood-opacity="0.25"/>'
        )
        return self.add_filter(shadow_id, shadow)

    def add_rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        rx: float = 0,
        **attrs: Any,
    ) -> "SVGBuilder":
        """Draws a rectangle."""
        rect_attrs: Dict[str, Any] = {"x": x, "y": y, "width": width, "height": height}
        if rx > 0:
            rect_attrs["rx"] = rx
        rect_attrs.update(attrs)
        self.elements.append(f"{self._indent()}<rect{self._format_attrs(rect_attrs)}/>")
        return self

    def add_text(self, content: str, x: float, y: float, **attrs: Any) -> "SVGBuilder":
        """Draws text."""
        text_attrs: Dict[str, Any] = {"x": x, "y": y}
        text_attrs.update(attrs)
        escaped = html.escape(content)
        self.elements.append(
            f"{self._indent()}<text{self._format_attrs(text_attrs)}>{escaped}</text>"
        )
        return self

    def begin_group(self, **attrs: Any) -> "SVGBuilder":
        """Opens a <g> tag."""
        self.elements.append(f"{self._indent()}<g{self._format_attrs(attrs)}>")
        self._indent_level += 1
        return self

    def end_group(self) -> "SVGBuilder":
        """Closes a <g> tag."""
        if self._indent_level > 1:
            self._indent_level -= 1
        self.elements.append(f"{self._indent()}</g>")
        return self

    def build(self) -> str:
        """Assembles the final SVG string."""
        defs_block = ""
        if self.defs:
            defs_content = "\n".join(self.defs)
            defs_block = f"  <defs>\n    {defs_content}\n  </defs>\n"

        elements_block = "\n".join(self.elements)

        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}">\n'
            f"{defs_block}"
            f'  <rect width="100%" height="100%" fill="{self.bg_color}"/>\n'
            f"{elements_block}\n"
            f"</svg>"
        )
        return svg
