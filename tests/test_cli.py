import subprocess
import sys


def test_cli_smoke_runs_independently_without_simulator(tmp_path):
    db_path = tmp_path / "smoke.sqlite3"

    result = subprocess.run(
        [sys.executable, "-m", "banking.cli", "smoke", "--db", str(db_path)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "smoke scenario passed" in result.stdout
    assert db_path.exists()
