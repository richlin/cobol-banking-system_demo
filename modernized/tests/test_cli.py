import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_cli_smoke_runs_independently_without_simulator(tmp_path):
    db_path = tmp_path / "smoke.sqlite3"
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(ROOT / "modernized")
    if existing_pythonpath:
        env["PYTHONPATH"] += os.pathsep + existing_pythonpath

    result = subprocess.run(
        [sys.executable, "-m", "banking.cli", "smoke", "--db", str(db_path)],
        check=False,
        text=True,
        capture_output=True,
        env=env,
    )

    assert result.returncode == 0
    assert "smoke scenario passed" in result.stdout
    assert db_path.exists()
