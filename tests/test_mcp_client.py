import os
import subprocess
import sys
from pathlib import Path


def test_stdio_client_walkthrough():
    script = Path(__file__).resolve().parents[1] / "examples/client_walkthrough.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, "BIONEMO_BACKEND": "simulated"},
    )
    assert completed.returncode == 0, completed.stderr
    assert "Simulator call succeeded" in completed.stdout
