"""Signatur der Wettkämpfe — in zwei Varianten, weil zwei verschiedene Dinge daran hängen.

    python scripts/data_signature.py all      → ALLE Meets, ohne Datumsfilter
    python scripts/data_signature.py window   → nur WIN_START <= Datum < WIN_END
    python scripts/data_signature.py          → wie "window" (Rückwärtskompatibilität)

Warum zwei:

* **all** treibt `.data_meets` und damit den `DATA_VERSION`-Bump, also den Redeploy.
  Der Redeploy startet den Streamlit-Prozess neu und ändert das Daten-Token — nur so
  bekommen die Loader neue Dateien überhaupt zu sehen. Bestenliste, Statistik und
  Rekorde nutzen All-Time-Daten, brauchen also auch nach Ende des Qualifikations-
  fensters weiterhin Updates (z. B. die SM-Ergebnisse selbst).

* **window** treibt `.last_data_update`, also das im Dashboard angezeigte Datum
  „Daten zuletzt aktualisiert". Das soll nur vorrücken, wenn sich etwas an den
  *qualifikationsrelevanten* Daten ändert — nicht bei OpenPowerlifting-Backfills
  alter Meets und nicht bei Wettkämpfen nach Fensterende.

Würde man beides aus derselben (gefensterten) Signatur speisen, gäbe es nach der SM
keinen Bump mehr → die All-Time-Seiten würden die SM-Ergebnisse nie zeigen.
"""
import csv
import glob
import os
import sys

# Müssen zum Qualifikationsfenster im Dashboard passen
# (QUAL_WINDOW_START / QUAL_WINDOW_END in my_analysis/oevk_dashboard.py).
WIN_START = "2025-09-05"
WIN_END = "2026-09-05"   # exklusiv: die SM selbst zählt nicht mehr zum Fenster


def in_window(date: str) -> bool:
    return bool(date) and WIN_START <= date < WIN_END


def build(mode: str) -> set:
    keep = (lambda d: bool(d)) if mode == "all" else in_window
    sig = set()

    # Nationale OeVK-Meets: Ordner mit meet.csv, Datum aus Zeile 2, Feld 2 (ISO).
    for m in glob.glob("meet-data/oevk/*/meet.csv"):
        try:
            with open(m, encoding="utf-8", errors="replace") as f:
                f.readline()
                row = f.readline().rstrip("\n").split(",")
            date = row[1] if len(row) > 1 else ""
            if keep(date):
                sig.add("nat:" + os.path.basename(os.path.dirname(m)) + ":" + date)
        except Exception:
            pass

    # Internationale Meets (EM/WM) aus der vorgefilterten CSV.
    intl = os.path.join("project-data", "oevk_intl.csv")
    if os.path.exists(intl):
        try:
            for r in csv.DictReader(open(intl, encoding="utf-8")):
                d = (r.get("_meet_date") or "").strip()
                if keep(d):
                    sig.add("intl:" + (r.get("_meet_name") or "").strip() + ":" + d)
        except Exception:
            pass

    return sig


def main() -> int:
    mode = (sys.argv[1] if len(sys.argv) > 1 else "window").strip().lower()
    if mode not in ("all", "window"):
        print(f"unknown mode {mode!r} — use 'all' or 'window'", file=sys.stderr)
        return 2
    sys.stdout.write("\n".join(sorted(build(mode))) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
