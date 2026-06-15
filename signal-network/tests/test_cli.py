"""Tests for the CLI entrypoint."""

import subprocess
import sys
from pathlib import Path


def test_cli_help():
    script = Path(__file__).parent.parent / "scripts" / "run_fanout.py"
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Signal Network regional fan-out" in result.stdout
    assert "--video" in result.stdout
    assert "--mock" in result.stdout
