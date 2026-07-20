"""The complete rendering pipeline implementation."""

import html
from typing import List

from github_profiler.domain.components import (
    ComponentBox,
    ComponentGroup,
    ComponentText,
    UIComponent,
)
from github_profiler.domain.interfaces import IComponentRenderer
from github_profiler.domain.theme import Theme


class MeasurementEngine:
    """Calculates implicit dimensions."""

    def measure(self, component: UIComponent) -> UIComponent:
        if isinstance(component, ComponentText):
            # Basic monospace measurement
            if getattr(component, "width", 0) == 0:
                component.width = len(component.content) * (
                    component.font_size * 0.6
                )

            if getattr(component, "height", 0) == 0:
                component.height = component.font_size + 6

        elif isinstance(component, ComponentGroup):
            for child in component.children:
                self.measure(child)

        return component


class LayoutEngine:
    """Calculates absolute X/Y positions."""

    def layout(self, component: UIComponent) -> UIComponent:
        if isinstance(component, ComponentGroup):
            current_y = component.y

            max_width = 0

            for child in component.children:
                # Preserve child offsets instead of overwriting them
                child.x = component.x + child.x
                child.y = current_y + child.y

                self.layout(child)

                current_y += getattr(child, "height", 20) + 10

                max_width = max(
                    max_width,
                    child.x + getattr(child, "width", 0),
                )

            component.height = current_y - component.y
            component.width = max_width - component.x

        return component


class TimelineOrchestrator:
    """Calculates sequential animation delays."""

    def sequence(self, component: UIComponent, delay: int = 0) -> int:
        component.animation_delay_ms = delay
        current_delay = delay

        if component.animation_type == "typewriter":
            if isinstance(component, ComponentText):
                current_delay += len(component.content) * 50

        elif component.animation_type == "fade-in":
            current_delay += 300

        if isinstance(component, ComponentGroup):
            for child in component.children:
                current_delay = self.sequence(child, current_delay)

        return current_delay


class SVGEngine(IComponentRenderer):
    """Final pipeline orchestrator and SVG generator."""

    def __init__(self) -> None:
        self.measurer = MeasurementEngine()
        self.layouter = LayoutEngine()
        self.timeline = TimelineOrchestrator()

    def _generate_css(self, theme: Theme) -> str:
        return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&amp;display=swap');

:root {{
    --bg: {theme.palette.background};
    --fg: {theme.palette.foreground};
    --primary: {theme.palette.primary};
}}

.container {{
    font-family: {theme.typography.font_stack};
    background: var(--bg);
}}

text {{
    fill: var(--fg);
    dominant-baseline: hanging;
}}

@keyframes typing {{
    from {{ width:0 }}
    to {{ width:100% }}
}}

@keyframes fadeIn {{
    from {{ opacity:0 }}
    to {{ opacity:1 }}
}}
</style>
"""

    def _render_node(self, component: UIComponent) -> str:
        attrs = " ".join(
            f'{k}="{html.escape(str(v))}"'
            for k, v in component.attributes.items()
        )

        style = ""

        if component.animation_type == "typewriter":
            duration = len(getattr(component, "content", "")) * 50

            style += (
                f"animation:typing {duration}ms steps(40,end) forwards;"
                f"animation-delay:{component.animation_delay_ms}ms;"
                "overflow:hidden;"
                "white-space:nowrap;"
            )

        elif component.animation_type == "fade-in":
            style += (
                "opacity:0;"
                f"animation:fadeIn 300ms forwards;"
                f"animation-delay:{component.animation_delay_ms}ms;"
            )

        if style:
            attrs += f' style="{style}"'

        if isinstance(component, ComponentBox):
            return (
                f'<rect '
                f'x="{component.x}" '
                f'y="{component.y}" '
                f'width="{component.width}" '
                f'height="{component.height}" '
                f'rx="{component.border_radius}" '
                f'fill="{component.fill_color}" '
                f'{attrs}/>'
            )

        elif isinstance(component, ComponentText):
            escaped = html.escape(component.content)

            return (
                f'<text '
                f'x="{component.x}" '
                f'y="{component.y}" '
                f'font-size="{component.font_size}" '
                f'font-weight="{component.font_weight}" '
                f'fill="{component.color}" '
                f'text-anchor="{component.text_anchor}" '
                f'{attrs}>'
                f'{escaped}'
                f'</text>'
            )

        elif isinstance(component, ComponentGroup):
            children_svg = "\n".join(
                self._render_node(child)
                for child in component.children
            )

            # IMPORTANT:
            # Children already have absolute coordinates.
            # Do NOT translate the group again.
            return f"<g {attrs}>\n{children_svg}\n</g>"

        return ""

    def _optimize(self, svg: str) -> str:
        return "\n".join(
            line.rstrip()
            for line in svg.splitlines()
            if line.strip()
        )

    def render(
        self,
        components: List[UIComponent],
        theme: Theme,
    ) -> str:

        root = ComponentGroup(
            children=components,
            x=0,
            y=0,
        )

        root = self.measurer.measure(root)
        root = self.layouter.layout(root)
        self.timeline.sequence(root)

        total_width = max(
            getattr(root, "width", 800),
            800,
        )

        total_height = max(
            getattr(root, "height", 600),
            600,
        )

        css = self._generate_css(theme)
        body = self._render_node(root)

        raw_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg
xmlns="http://www.w3.org/2000/svg"
width="{total_width}"
height="{total_height}"
viewBox="0 0 {total_width} {total_height}"
class="container">

{css}

<rect
width="100%"
height="100%"
fill="{theme.palette.background}"/>

{body}

</svg>
"""

        return self._optimize(raw_svg)