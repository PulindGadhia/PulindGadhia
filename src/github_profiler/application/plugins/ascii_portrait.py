"""ASCII Portrait Plugin."""

import io
from typing import List

import requests
from PIL import Image

try:
    from rembg import remove
except (ImportError, SystemExit):
    # Fallback if rembg is not available
    def remove(data: bytes) -> bytes:
        return data


from github_profiler.domain.components import (
    Canvas,
    ComponentBox,
    ComponentText,
    UIComponent,
)
from github_profiler.domain.interfaces import IProfilePlugin
from github_profiler.domain.models import GitHubUser
from github_profiler.domain.theme import Theme

# 11 characters from darkest to lightest
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]


class AsciiPortraitPlugin(IProfilePlugin):
    """Generates an ASCII art portrait from the user's avatar."""

    def __init__(self, width: int = 40, remove_bg: bool = True) -> None:
        self.output_width = width
        self.remove_bg = remove_bg

    @property
    def name(self) -> str:
        return "ascii_portrait"

    @property
    def pipeline(self) -> str:
        return "dashboard"

    def _fetch_avatar(self, url: str) -> bytes:
        if not url:
            return b""
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            return resp.content
        except requests.RequestException:
            return b""

    def _image_to_ascii(self, image_bytes: bytes) -> List[str]:
        if not image_bytes:
            return ["No Avatar"]

        try:
            if self.remove_bg:
                image_bytes = remove(image_bytes)

            img = Image.open(io.BytesIO(image_bytes)).convert("L")

            # Resize
            width, height = img.size
            aspect_ratio = height / width
            # ASCII characters are roughly twice as tall as they are wide
            new_height = int(self.output_width * aspect_ratio * 0.5)
            if new_height == 0:
                new_height = 1
            img = img.resize((self.output_width, new_height))

            # Convert to ASCII
            pixels = img.tobytes()
            # Map 0-255 to 0-10 index
            new_pixels = [ASCII_CHARS[pixel // 25] for pixel in pixels]
            new_pixels_str = "".join(new_pixels)

            # Split into lines
            return [
                new_pixels_str[i : i + self.output_width]
                for i in range(0, len(new_pixels_str), self.output_width)
            ]
        except Exception:
            return ["Error parsing avatar"]

    def generate(self, user: GitHubUser, theme: Theme) -> UIComponent:
        lines = self._image_to_ascii(self._fetch_avatar(user.avatar_url))

        group = Canvas(x=0, y=0)

        bg = ComponentBox(
            width=self.output_width * 10,
            height=len(lines) * 12 + 20,
            fill_color=theme.palette.background,
            border_radius=theme.window.border_radius,
            stroke_color=theme.window.border_color,
            stroke_width=1,
        )
        group.children.append(bg)

        for i, text in enumerate(lines):
            line_comp = ComponentText(
                content=text,
                x=10,
                y=20 + i * 12,
                color=theme.palette.foreground,
                font_size=theme.typography.small_size,
                animation_type="fade-in",
                animation_delay_ms=i * 20,
            )
            group.children.append(line_comp)

        return group


def get_plugin() -> IProfilePlugin:
    """Plugin entry point."""
    return AsciiPortraitPlugin()
