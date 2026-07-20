"""
scripts.common.exceptions
=========================

Centralized exception hierarchy for the GitHub Profile Generator.

Every project-specific exception should inherit from ``GitHubProfileError``.
This allows callers to catch a single base exception when appropriate while
still preserving more specific exception types for fine-grained handling.

Example:
    >>> from scripts.common.exceptions import ConfigurationError
    >>> raise ConfigurationError("Missing GitHub token")
"""

from __future__ import annotations

from typing import Optional


class GitHubProfileError(Exception):
    """
    Base class for all project-specific exceptions.

    Attributes:
        message:
            Human-readable error message.
    """

    def __init__(self, message: str = "An unknown project error occurred.") -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class ConfigurationError(GitHubProfileError):
    """Raised when configuration is invalid or incomplete."""


class EnvironmentVariableError(ConfigurationError):
    """Raised when a required environment variable is missing."""


class FileOperationError(GitHubProfileError):
    """Raised when reading or writing files fails."""


class DirectoryCreationError(FileOperationError):
    """Raised when a directory cannot be created."""


class ImageProcessingError(GitHubProfileError):
    """Raised when image processing fails."""


class SVGGenerationError(GitHubProfileError):
    """Raised when SVG generation fails."""


class AnimationError(GitHubProfileError):
    """Raised when animation generation fails."""


class ASCIIConversionError(GitHubProfileError):
    """Raised when ASCII conversion fails."""


class HeatmapGenerationError(GitHubProfileError):
    """Raised when contribution heatmap generation fails."""


class InfoCardGenerationError(GitHubProfileError):
    """Raised when the information card cannot be generated."""


class ReadmeGenerationError(GitHubProfileError):
    """Raised when README generation fails."""


class GitHubAPIError(GitHubProfileError):
    """
    Raised when communication with the GitHub API fails.

    Attributes:
        status_code:
            HTTP status code returned by GitHub.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
    ) -> None:
        self.status_code = status_code

        if status_code is not None:
            message = f"[HTTP {status_code}] {message}"

        super().__init__(message)


class RateLimitExceededError(GitHubAPIError):
    """Raised when the GitHub API rate limit has been exceeded."""


class ValidationError(GitHubProfileError):
    """Raised when user input or configuration validation fails."""


class TemplateError(GitHubProfileError):
    """Raised when rendering a template fails."""


class CacheError(GitHubProfileError):
    """Raised when cache operations fail."""


class CLIError(GitHubProfileError):
    """Raised for command-line interface related failures."""