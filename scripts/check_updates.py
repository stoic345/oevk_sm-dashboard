"""Pull latest OpenPowerlifting / OpenIPF data and update freshness markers.

Run manually or on a schedule (cron / Windows Task Scheduler / GitHub Action).

ALWAYS touches `.last_check` — that marker drives the dashboard's
"Zuletzt nach Updates gesucht"-Anzeige and just records that we LOOKED.

Touches `.last_data_update` ONLY when the pull brought in real changes inside
`meet-data/oevk/` — that marker drives "Daten zuletzt aktualisiert".
"""

from __future__ import annotations
import datetime as _dt
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK_MARKER = ROOT / ".last_check"
DATA_MARKER = ROOT / ".last_data_update"
OEVK_DIR = ROOT / "meet-data" / "oevk"


def write_timestamp(path: Path) -> None:
    path.write_text(_dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n")


def run_git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    try:
        res = subprocess.run(
            ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=120,
        )
        return res.returncode, res.stdout, res.stderr
    except FileNotFoundError:
        return 127, "", "git not installed"
    except subprocess.TimeoutExpired:
        return 124, "", "git timed out"


def main() -> int:
    if not (ROOT / ".git").exists():
        print(f"[check_updates] no .git in {ROOT} — only touching {CHECK_MARKER.name}")
        write_timestamp(CHECK_MARKER)
        return 0

    # Snapshot HEAD before pull so we can ask git whether oevk files changed.
    rc, head_before, _ = run_git(["rev-parse", "HEAD"], ROOT)
    if rc != 0:
        print("[check_updates] could not read HEAD — aborting", file=sys.stderr)
        return rc
    head_before = head_before.strip()

    rc, out, err = run_git(["pull", "--ff-only"], ROOT)
    print(out.strip() or "(no stdout)")
    if err.strip():
        print(err.strip(), file=sys.stderr)
    if rc != 0:
        print(f"[check_updates] git pull failed (rc={rc}), still touching {CHECK_MARKER.name}")
        write_timestamp(CHECK_MARKER)
        return rc

    rc2, head_after, _ = run_git(["rev-parse", "HEAD"], ROOT)
    head_after = head_after.strip() if rc2 == 0 else head_before

    # Diff between old and new HEAD, restricted to the OeVK directory.
    real_data_change = False
    if head_after != head_before:
        rc3, names, _ = run_git(
            ["diff", "--name-only", head_before, head_after, "--", "meet-data/oevk/"],
            ROOT,
        )
        if rc3 == 0 and names.strip():
            real_data_change = True

    write_timestamp(CHECK_MARKER)
    print(f"[check_updates] touched {CHECK_MARKER.name}")

    if real_data_change:
        write_timestamp(DATA_MARKER)
        print(f"[check_updates] OeVK data changed — touched {DATA_MARKER.name}")
    else:
        print("[check_updates] no OeVK data changes in this pull")

    return 0


if __name__ == "__main__":
    sys.exit(main())
