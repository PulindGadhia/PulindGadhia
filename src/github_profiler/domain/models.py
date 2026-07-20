"""Domain models for the GitHub Profiler application.

This module contains the core entities and business objects for the application,
implemented as dataclasses with slots enabled for memory efficiency.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass(slots=True)
class ContributionDay:
    """Represents a single day of contributions on GitHub.

    Attributes:
        date: The calendar date of the contributions.
        contribution_count: The number of contributions made on this day.
        color: The hex color code representing the contribution level.
    """

    date: date
    contribution_count: int
    color: str


@dataclass(slots=True)
class Repository:
    """Represents a GitHub repository.

    Attributes:
        name: The name of the repository.
        description: A brief description of the repository.
        primary_language: The primary programming language used.
        stargazer_count: The number of stars the repository has received.
        fork_count: The number of forks of the repository.
        url: The URL to the repository.
    """

    name: str
    description: Optional[str]
    primary_language: Optional[str]
    stargazer_count: int
    fork_count: int
    url: str


@dataclass(slots=True)
class ProfileStats:
    """Aggregated statistics for a GitHub user.

    Attributes:
        total_contributions: Total contributions in the past year.
        total_repositories: Total public repositories owned by the user.
        total_stars: Total stars received across all repositories.
        total_pull_requests: Total pull requests created.
        total_issues: Total issues created.
    """

    total_contributions: int = 0
    total_repositories: int = 0
    total_stars: int = 0
    total_pull_requests: int = 0
    total_issues: int = 0


@dataclass(slots=True)
class GitHubUser:
    """Represents a GitHub user and their profile data.

    Attributes:
        username: The user's GitHub login handle.
        name: The user's display name.
        bio: The user's biography or profile description.
        avatar_url: The URL to the user's avatar image.
        company: The user's associated company.
        location: The user's geographical location.
        followers: The number of followers the user has.
        following: The number of people the user is following.
        stats: Aggregated statistics for the user's profile.
        contribution_calendar: A list of daily contributions over the past year.
        top_repositories: A list of the user's top repositories (usually by stars).
    """

    username: str
    name: Optional[str]
    bio: Optional[str]
    avatar_url: str
    company: Optional[str]
    location: Optional[str]
    followers: int
    following: int
    stats: ProfileStats = field(default_factory=ProfileStats)
    contribution_calendar: List[ContributionDay] = field(default_factory=list)
    top_repositories: List[Repository] = field(default_factory=list)
