"""GitHub GraphQL client implementation.

This module implements the IGitHubClient interface using the GitHub GraphQL API.
It requires a Personal Access Token (PAT) for authentication.
"""

import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from github_profiler.domain.interfaces import IGitHubClient
from github_profiler.domain.models import (
    ContributionDay,
    GitHubUser,
    ProfileStats,
    Repository,
)

logger = logging.getLogger(__name__)


class GitHubGraphQLClient(IGitHubClient):
    """Client for fetching user data from the GitHub GraphQL API."""

    URL = "https://api.github.com/graphql"

    def __init__(self, token: Optional[str] = None) -> None:
        """Initializes the GraphQL client.

        Args:
            token: The GitHub Personal Access Token. If not provided, it will
                attempt to read from the GITHUB_TOKEN environment variable.

        Raises:
            ValueError: If no token is provided or found in the environment.
        """
        self._token = token or os.environ.get("GITHUB_TOKEN")
        if not self._token:
            raise ValueError(
                "A GitHub token must be provided or set in the "
                "GITHUB_TOKEN environment variable."
            )
        self._headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def fetch_user_data(self, username: str) -> GitHubUser:
        """Fetches complete profile data for a GitHub user.

        Args:
            username: The GitHub username to fetch.

        Returns:
            A populated GitHubUser instance.

        Raises:
            RuntimeError: If the GraphQL request fails or returns errors.
        """
        logger.info(f"Fetching GitHub data for user: {username}")

        query = self._build_query()
        variables = {"username": username}

        response = requests.post(
            self.URL,
            json={"query": query, "variables": variables},
            headers=self._headers,
            timeout=10,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"GitHub API request failed: {response.status_code} {response.text}"
            )

        data = response.json()
        if "errors" in data:
            raise RuntimeError(f"GitHub GraphQL errors: {data['errors']}")

        user_data = data.get("data", {}).get("user")
        if not user_data:
            raise RuntimeError(f"User '{username}' not found.")

        return self._parse_user_data(user_data)

    def _build_query(self) -> str:
        """Builds the GraphQL query string for user data.

        Returns:
            The GraphQL query as a string.
        """
        return """
        query($username: String!) {
          user(login: $username) {
            login
            name
            bio
            avatarUrl
            company
            location
            followers {
              totalCount
            }
            following {
              totalCount
            }
            repositories(first: 6, orderBy: {field: STARGAZERS, direction: DESC}, isFork: false) {
              totalCount
              nodes {
                name
                description
                primaryLanguage {
                  name
                }
                stargazerCount
                forkCount
                url
              }
            }
            pullRequests(first: 1) {
              totalCount
            }
            issues(first: 1) {
              totalCount
            }
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    date
                    color
                  }
                }
              }
            }
          }
        }
        """

    def _parse_user_data(self, user_data: Dict[str, Any]) -> GitHubUser:
        """Parses the raw GraphQL JSON response into domain models.

        Args:
            user_data: The JSON dictionary containing the 'user' object data.

        Returns:
            A populated GitHubUser object.
        """
        # Parse basic info
        username = user_data.get("login", "")
        name = user_data.get("name")
        bio = user_data.get("bio")
        avatar_url = user_data.get("avatarUrl", "")
        company = user_data.get("company")
        location = user_data.get("location")
        followers = user_data.get("followers", {}).get("totalCount", 0)
        following = user_data.get("following", {}).get("totalCount", 0)

        # Parse stats
        repos_data = user_data.get("repositories", {})
        total_repos = repos_data.get("totalCount", 0)
        total_prs = user_data.get("pullRequests", {}).get("totalCount", 0)
        total_issues = user_data.get("issues", {}).get("totalCount", 0)

        contrib_collection = user_data.get("contributionsCollection", {})
        contrib_calendar = contrib_collection.get("contributionCalendar", {})
        total_contributions = contrib_calendar.get("totalContributions", 0)

        # Parse repositories
        top_repositories: List[Repository] = []
        total_stars = 0
        for repo_node in repos_data.get("nodes", []):
            if not repo_node:
                continue
            primary_language = None
            lang_node = repo_node.get("primaryLanguage")
            if lang_node:
                primary_language = lang_node.get("name")

            repo = Repository(
                name=repo_node.get("name", ""),
                description=repo_node.get("description"),
                primary_language=primary_language,
                stargazer_count=repo_node.get("stargazerCount", 0),
                fork_count=repo_node.get("forkCount", 0),
                url=repo_node.get("url", ""),
            )
            top_repositories.append(repo)
            total_stars += repo.stargazer_count

        stats = ProfileStats(
            total_contributions=total_contributions,
            total_repositories=total_repos,
            total_stars=total_stars,
            total_pull_requests=total_prs,
            total_issues=total_issues,
        )

        # Parse contribution calendar
        contribution_days: List[ContributionDay] = []
        for week in contrib_calendar.get("weeks", []):
            for day in week.get("contributionDays", []):
                date_str = day.get("date")
                if not date_str:
                    continue
                dt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                contrib_day = ContributionDay(
                    date=dt_date,
                    contribution_count=day.get("contributionCount", 0),
                    color=day.get("color", "#ebedf0"),
                )
                contribution_days.append(contrib_day)

        return GitHubUser(
            username=username,
            name=name,
            bio=bio,
            avatar_url=avatar_url,
            company=company,
            location=location,
            followers=followers,
            following=following,
            stats=stats,
            contribution_calendar=contribution_days,
            top_repositories=top_repositories,
        )
