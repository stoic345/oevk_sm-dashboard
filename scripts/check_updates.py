"""Pull latest OpenPowerlifting / OpenIPF data and update freshness markers.

Run manually or on a schedule (cron / Windows Task Scheduler / GitHub Action).

Always touches `.last_check` to record the check time, even if nothing new was
pulled. If `git pull` brought in new commits, the meet CSV mtimes will advance
on their own, which is what `Daten zuletzt aktualisiert` reads.
"""

from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = ROOT / ".last_check"


def touch(path: Path) -> None:
    path.touch(exist_ok=True)
    os.utime(path, None)


def git_pull(cwd: Path) -> int:
    """Run `git pull --ff-only` if cwd is a git repo. Returns the exit code, or -1 if not a repo."""
    if not (cwd / ".git").exists():
        print(f"[check_updates] no .git in {cwd} — skipping pull")
        return -1
    try:
        res = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=120,
        )
        print(res.stdout.strip() or "(no stdout)")
        if res.stderr.strip():
            print(res.stderr.strip(), file=sys.stderr)
        return res.returncode
    except FileNotFoundError:
        print("[check_updates] git not installed", file=sys.stderr)
        return 127
    except subprocess.TimeoutExpired:
        print("[check_updates] git pull timed out", file=sys.stderr)
        return 124


def main() -> int:
    rc = git_pull(ROOT)
    # Always touch the marker so the dashboard knows we checked, regardless of
    # whether new commits arrived.
    touch(MARKER)
    print(f"[check_updates] touched {MARKER}")
    return 0 if rc in (0, -1) else rc


if __name__ == "__main__":
    sys.exit(main())
