"""The Guide page tells people to run `python -m ed_narrator_mcp`: that exact form must start (and answer --help), not just import."""
import subprocess
import sys


def test_python_dash_m_runs_the_server_entry_point():
    r = subprocess.run([sys.executable, "-m", "ed_narrator_mcp", "--help"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    assert "ed-narrator-mcp" in r.stdout
