"""Domain interfaces for v2.0 Clean Architecture."""

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional

from github_profiler.domain.components import UIComponent
from github_profiler.domain.events import Event
from github_profiler.domain.models import GitHubUser
from github_profiler.domain.theme import Theme


class IGitHubClient(ABC):
    """Interface for fetching profile data from GitHub."""

    @abstractmethod
    def fetch_user_data(self, username: str) -> GitHubUser:
        """Fetches complete profile data.

        Args:
            username: The GitHub login.

        Returns:
            The populated GitHubUser domain entity.
        """
        pass


class ICache(ABC):
    """Interface for infrastructure caching."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieves an item from the cache.

        Args:
            key: Cache key.

        Returns:
            The cached object or None if missing/expired.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Stores an item in the cache.

        Args:
            key: Cache key.
            value: Data to store.
            ttl_seconds: Time-To-Live in seconds.
        """
        pass


class IEventBus(ABC):
    """Interface for the publish-subscribe event bus."""

    @abstractmethod
    def subscribe(self, event_name: str, callback: Callable[[Event], None]) -> None:
        """Subscribes a callback to an event.

        Args:
            event_name: The event to listen for.
            callback: The function to execute.
        """
        pass

    @abstractmethod
    def publish(self, event: Event) -> None:
        """Publishes an event to all subscribers.

        Args:
            event: The Event instance to broadcast.
        """
        pass


class IProfilePlugin(ABC):
    """Interface for visual plugins."""

    @abstractmethod
    def generate(self, user: GitHubUser, theme: Theme) -> UIComponent:
        """Generates the UIComponent structure for this plugin's section.

        Args:
            user: The loaded GitHub user data.
            theme: The injected theme rules.

        Returns:
            The root UIComponent representing this plugin.
        """
        pass


class IPluginLoader(ABC):
    """Interface for dynamic plugin discovery."""

    @abstractmethod
    def load_plugins(self, plugin_names: List[str]) -> List[IProfilePlugin]:
        """Loads and instantiates plugins by name.

        Args:
            plugin_names: List of plugin identifiers.

        Returns:
            List of instantiated IProfilePlugin objects.
        """
        pass


class IComponentRenderer(ABC):
    """Interface for formatting UIComponents into final output strings (e.g., SVG)."""

    @abstractmethod
    def render(self, components: List[UIComponent], theme: Theme) -> str:
        """Renders the abstract component tree into a string.

        Args:
            components: The components to render.
            theme: Theme for global CSS/styling.

        Returns:
            The rendered string.
        """
        pass


class IImageProcessor(ABC):
    """Interface for complex image operations (e.g., ASCII conversion)."""

    @abstractmethod
    def process_image(self, image_url: str) -> str:
        """Processes an image from a URL.

        Args:
            image_url: The source image URL.

        Returns:
            The processed string result.
        """
        pass
