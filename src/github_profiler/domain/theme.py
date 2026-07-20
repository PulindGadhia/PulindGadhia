"""Domain models for theming."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Palette:
    """Color palette for a theme."""

    background: str = "#0d1117"
    foreground: str = "#c9d1d9"
    primary: str = "#58a6ff"
    secondary: str = "#30363d"
    success: str = "#2ea043"


@dataclass(slots=True)
class Typography:
    """Typography configuration."""

    font_stack: str = (
        'ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace'
    )
    title_size: int = 18
    text_size: int = 14
    small_size: int = 10


@dataclass(slots=True)
class Window:
    """Window dressing and borders."""

    border_radius: int = 8
    border_color: str = "#30363d"
    show_mac_dots: bool = True


@dataclass(slots=True)
class Cursor:
    """Terminal typing cursor settings."""

    char: str = "_"
    color: str = "#58a6ff"
    blink_rate: float = 0.5


@dataclass(slots=True)
class Animation:
    """Global animation settings."""

    enabled: bool = True
    typing_speed_ms: int = 50
    fade_duration_ms: int = 300


@dataclass(slots=True)
class Theme:
    """Complete theme definition containing all visual configuration."""

    palette: Palette = field(default_factory=Palette)
    typography: Typography = field(default_factory=Typography)
    window: Window = field(default_factory=Window)
    cursor: Cursor = field(default_factory=Cursor)
    animation: Animation = field(default_factory=Animation)
