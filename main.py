"""Main entry point for GitHub Profiler."""

import sys
from pathlib import Path

# Ensure src is in the python path for local execution before packaging
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from github_profiler.presentation.cli import run_cli  # noqa: E402

if __name__ == "__main__":
    sys.exit(run_cli())
