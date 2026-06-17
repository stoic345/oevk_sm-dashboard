"""Pre-filter EM/WM entries to Austrian lifters and write a small CSV.

Run locally OR in the daily GitHub Actions workflow. Produces:
    project-data/oevk_intl.csv

Schema = all entries.csv columns + `_meet_name`, `_meet_date`. The dashboard's
`load_international_for_austrians()` reads this file when `meet-data/ipf/` and
`meet-data/epf/` are not present (e.g. on Streamlit Cloud, where we don't ship
the full opl-data fork).

Identity match key: (diacritic-stripped lowercased Name, Sex, BirthYear),
built from every entry in `meet-data/oevk/`. Equipment filter: Raw only.

CLI:
    python scripts/build_intl_csv.py [--repo-root PATH]

Exit 0 always (no-data scenario is a valid output: an empty CSV with header).
"""
from __future__ import annotations

import argparse
import csv
import sys
import unicodedata
from pathlib import Path


def norm_name(s: str) -> str:
    if not s:
        return ""
    return (
        unicodedata.normalize("NFKD", str(s))
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .strip()
    )


def build_austrian_identity_set(oevk_dir: Path) -> set:
    """Walk meet-data/oevk/ and harvest unique (norm_name, sex, birth_year) triples."""
    out: set = set()
    if not oevk_dir.exists():
        return out
    for folder in oevk_dir.iterdir():
        e = folder / "entries.csv"
        if not e.is_file():
            continue
        try:
            with e.open(encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                for r in reader:
                    nm = norm_name(r.get("Name", ""))
                    sx = (r.get("Sex") or "").strip().upper()
                    by = (r.get("BirthYear") or "").strip()
                    if nm and sx and by and by.lower() != "nan":
                        out.add((nm, sx, by))
        except Exception as ex:
            print(f"WARN read {e}: {ex}", file=sys.stderr)
    return out


def read_meet_meta(meet_csv: Path) -> tuple[str, str]:
    """Return (m_date, m_name) from meet.csv — best-effort."""
    try:
        with meet_csv.open(encoding="utf-8", errors="replace") as fh:
            fh.readline()
            fields = fh.readline().rstrip("\n").split(",")
        m_date = fields[1] if len(fields) > 1 else ""
        m_name = fields[5] if len(fields) > 5 else meet_csv.parent.name
        return m_date, m_name
    except Exception:
        return "", meet_csv.parent.name


def collect_intl_rows(intl_dirs: list[Path], austrians: set) -> tuple[list[dict], list[str]]:
    """Walk intl federations (ipf, epf), keep RAW rows whose identity ∈ austrians.

    Returns (rows, fieldnames). fieldnames = union of seen columns + meet meta.
    """
    rows: list[dict] = []
    fieldnames: list[str] = []
    seen_cols: set = set()
    for root in intl_dirs:
        if not root.exists():
            continue
        for folder in root.iterdir():
            if not folder.is_dir():
                continue
            e_file = folder / "entries.csv"
            m_file = folder / "meet.csv"
            if not (e_file.is_file() and m_file.is_file()):
                continue
            m_date, m_name = read_meet_meta(m_file)
            try:
                with e_file.open(encoding="utf-8", newline="") as fh:
                    reader = csv.DictReader(fh)
                    for r in reader:
                        if (r.get("Equipment") or "").strip() != "Raw":
                            continue
                        key = (
                            norm_name(r.get("Name", "")),
                            (r.get("Sex") or "").strip().upper(),
                            (r.get("BirthYear") or "").strip(),
                        )
                        if key not in austrians:
                            continue
                        r["_meet_name"] = m_name
                        r["_meet_date"] = m_date
                        rows.append(r)
                        # accumulate column order from first observed row
                        for k in r.keys():
                            if k not in seen_cols:
                                seen_cols.add(k)
                                fieldnames.append(k)
            except Exception as ex:
                print(f"WARN read {e_file}: {ex}", file=sys.stderr)
    # Ensure meta columns are at the end if not yet present
    for k in ("_meet_name", "_meet_date"):
        if k not in fieldnames:
            fieldnames.append(k)
    return rows, fieldnames


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=None,
                    help="repo root (default: script's parent's parent)")
    args = ap.parse_args()

    repo_root = Path(args.repo_root) if args.repo_root else Path(__file__).resolve().parent.parent
    oevk_dir = repo_root / "meet-data" / "oevk"
    intl_dirs = [repo_root / "meet-data" / "ipf", repo_root / "meet-data" / "epf"]
    out_csv = repo_root / "project-data" / "oevk_intl.csv"

    austrians = build_austrian_identity_set(oevk_dir)
    print(f"[build_intl_csv] Austrian identities (Name, Sex, BirthYear): {len(austrians)}")

    rows, fieldnames = collect_intl_rows(intl_dirs, austrians)
    print(f"[build_intl_csv] EM/WM rows kept (Raw, Austrians): {len(rows)}")

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    sz = out_csv.stat().st_size
    print(f"[build_intl_csv] Wrote {out_csv} ({sz / 1024:.1f} KB, {len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
