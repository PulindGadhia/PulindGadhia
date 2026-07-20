"""Neofetch Plugin for GitHub Profiler."""

from github_profiler.domain.components import (
    ComponentBox,
    ComponentGroup,
    ComponentText,
    UIComponent,
)
from github_profiler.domain.interfaces import IProfilePlugin
from github_profiler.domain.models import GitHubUser
from github_profiler.domain.theme import Theme


class NeofetchPlugin(IProfilePlugin):
    """Generates a terminal-style neofetch output for a GitHub user."""

    @property
    def name(self) -> str:
        return "neofetch"

    def generate(self, user: GitHubUser, theme: Theme) -> UIComponent:
        """Generates the neofetch UIComponent tree."""
        lines = [
            f"{user.username}@github",
            "-" * (len(user.username) + 7),
            "OS: GitHub Profile",
            f"Host: github.com/{user.username}",
            f"Followers: {user.followers}",
            f"Following: {user.following}",
            f"Repos: {user.stats.total_repositories}",
        ]

        group = ComponentGroup(x=0, y=0)

        # Terminal Background
        bg = ComponentBox(
            width=400,
            height=len(lines) * 20 + 40,
            fill_color=theme.palette.background,
            border_radius=theme.window.border_radius,
            stroke_color=theme.window.border_color,
            stroke_width=1,
        )
        group.children.append(bg)

        # Text lines
        for i, text in enumerate(lines):
            line_comp = ComponentText(
                content=text,
                x=20,
                y=30 + i * 20,
                color=theme.palette.primary,
                font_size=theme.typography.text_size,
                animation_type="typewriter",
            )
            group.children.append(line_comp)

        return group


def get_plugin() -> IProfilePlugin:
    """Plugin entry point for FilesystemPluginLoader."""
    return NeofetchPlugin()
