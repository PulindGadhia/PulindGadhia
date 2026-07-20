import pytest
from pytest import CaptureFixture
from github_profiler.presentation.cli import run_cli


def test_cli_help(capsys: CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        run_cli(["--help"])
    captured = capsys.readouterr()
    assert "GitHub Profiler v2.0" in captured.out
