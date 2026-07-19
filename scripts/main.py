"""
Profile Terminal

Main Entry Point

Author:
    Pulind Gadhia

Description:
    Builds all assets required for the GitHub profile.
"""

from pathlib import Path

from common.logger import get_logger


logger = get_logger(__name__)


def main() -> None:
    """Main application entry point."""

    project_root = Path(__file__).resolve().parent.parent

    logger.info("Profile Terminal")
    logger.info("Project Root: %s", project_root)

    logger.info("Build pipeline will be implemented in upcoming milestones.")


if __name__ == "__main__":
    main()