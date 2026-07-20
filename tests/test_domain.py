"""Unit tests for the domain models."""
from datetime import date
from github_profiler.domain.models import (
    ContributionDay,
    GitHubUser,
    ProfileStats,
    Repository,
)


def test_contribution_day_creation() -> None:
    """Test creation of a ContributionDay."""
    c = ContributionDay(date=date(2023, 1, 1), contribution_count=5, color="#ff0000")
    assert c.date == date(2023, 1, 1)
    assert c.contribution_count == 5
    assert c.color == "#ff0000"


def test_repository_creation() -> None:
    """Test creation of a Repository."""
    r = Repository(
        name="test-repo",
        description="A test repository",
        primary_language="Python",
        stargazer_count=100,
        fork_count=10,
        url="https://github.com/user/test-repo",
    )
    assert r.name == "test-repo"
    assert r.primary_language == "Python"
    assert r.stargazer_count == 100


def test_profile_stats_defaults() -> None:
    """Test ProfileStats default values."""
    s = ProfileStats()
    assert s.total_contributions == 0
    assert s.total_repositories == 0
    assert s.total_stars == 0


def test_github_user_creation() -> None:
    """Test creation of a GitHubUser."""
    u = GitHubUser(
        username="octocat",
        name="Mona Lisa Octocat",
        bio="I am a cat",
        avatar_url="https://github.com/octocat.png",
        company="@github",
        location="San Francisco",
        followers=1000,
        following=10,
    )
    assert u.username == "octocat"
    assert u.name == "Mona Lisa Octocat"
    assert u.followers == 1000
    assert len(u.top_repositories) == 0
    assert len(u.contribution_calendar) == 0
