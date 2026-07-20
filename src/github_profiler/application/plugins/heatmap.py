"""Contribution Heatmap Plugin."""

from github_profiler.domain.components import ComponentBox, ComponentGroup, UIComponent
from github_profiler.domain.interfaces import IProfilePlugin
from github_profiler.domain.models import GitHubUser
from github_profiler.domain.theme import Theme


class HeatmapPlugin(IProfilePlugin):
    """Generates a GitHub-style contribution heatmap."""

    @property
    def name(self) -> str:
        return "heatmap"

    def generate(self, user: GitHubUser, theme: Theme) -> UIComponent:
        CELL_SIZE = 10
        CELL_GAP = 4

        group = ComponentGroup(x=0, y=0)

        # We assume contribution_calendar is sorted chronologically
        days = user.contribution_calendar

        # Calculate total dimensions
        num_weeks = (len(days) + 6) // 7
        total_width = num_weeks * (CELL_SIZE + CELL_GAP) + CELL_GAP
        total_height = 7 * (CELL_SIZE + CELL_GAP) + CELL_GAP

        # Background
        bg = ComponentBox(
            width=total_width,
            height=total_height,
            fill_color=theme.palette.background,
            border_radius=theme.window.border_radius,
            stroke_color=theme.window.border_color,
            stroke_width=1,
        )
        group.children.append(bg)

        # Chunk into weeks (columns)
        weeks = [days[i : i + 7] for i in range(0, len(days), 7)]

        for week_idx, week in enumerate(weeks):
            for day_idx, day in enumerate(week):
                # Theme-aware empty cells
                color = (
                    day.color if day.contribution_count > 0 else theme.palette.secondary
                )

                # Tooltip for future-ready metadata
                tooltip = f"{day.contribution_count} contributions on {day.date}"

                cell = ComponentBox(
                    width=CELL_SIZE,
                    height=CELL_SIZE,
                    x=CELL_GAP + week_idx * (CELL_SIZE + CELL_GAP),
                    y=CELL_GAP + day_idx * (CELL_SIZE + CELL_GAP),
                    fill_color=color,
                    border_radius=2,
                    attributes={"data-tooltip": tooltip, "title": tooltip},
                    animation_type="fade-in",
                    animation_delay_ms=week_idx * 15,  # Cascade per column
                )
                group.children.append(cell)

        return group


def get_plugin() -> IProfilePlugin:
    """Plugin entry point."""
    return HeatmapPlugin()
