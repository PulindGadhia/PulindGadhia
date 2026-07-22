"""Domain geometry and measurement models for V3."""

from dataclasses import dataclass


@dataclass(slots=True)
class Point:
    """A 2D coordinate in space."""

    x: float = 0.0
    y: float = 0.0


@dataclass(slots=True)
class Size:
    """A 2D dimension."""

    width: float = 0.0
    height: float = 0.0


@dataclass(slots=True)
class Margin:
    """Margin spacing (outside boundary)."""

    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0
    left: float = 0.0

    @classmethod
    def all(cls, value: float) -> "Margin":
        """Helper to create uniform margin."""
        return cls(value, value, value, value)


@dataclass(slots=True)
class Padding:
    """Padding spacing (inside boundary)."""

    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0
    left: float = 0.0

    @classmethod
    def all(cls, value: float) -> "Padding":
        """Helper to create uniform padding."""
        return cls(value, value, value, value)


@dataclass(slots=True)
class Rectangle:
    """A complete geometric bounding box."""

    origin: Point
    size: Size
