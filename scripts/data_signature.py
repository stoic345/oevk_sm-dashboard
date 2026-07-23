"""Signatur der *dashboard-relevanten* Wettkämpfe (im Qualifikationsfenster).

Gibt je Wettkampf eine Zeile aus (national + international), aber NUR für Meets
mit Datum >= WIN_START. Damit ändert sich die Signatur ausschließlich, wenn ein
neuer aktueller Wettkampf hinzukommt — nicht bei OpenPowerlifting-Backfills alter
Meets oder täglichem Re-Processing bestehender Ergebnisse.

Der Sync-Workflow vergleicht die Ausgabe mit der committeten .data_meets und
schreibt .last_data_update nur bei echter Änderung.
"""
import csv
import glob
import os
import sys

# Muss zum Qualifikationsfenster im Dashboard passen (QUAL_WINDOW_START).
WIN_START = "2025-09-05"

sig = set()

# Nationale OeVK-Meets: Ordner mit meet.csv, Datum aus Zeile 2, Feld 2 (ISO).
for m in glob.glob("meet-data/oevk/*/meet.csv"):
    try:
        with open(m, encoding="utf-8", errors="replace") as f:
            f.readline()
            row = f.readline().rstrip("\n").split(",")
        date = row[1] if len(row) > 1 else ""
        if date >= WIN_START:
            sig.add("nat:" + os.path.basename(os.path.dirname(m)) + ":" + date)
    except Exception:
        pass

# Internationale Meets (EM/WM) aus der vorgefilterten CSV.
intl = os.path.join("project-data", "oevk_intl.csv")
if os.path.exists(intl):
    try:
        for r in csv.DictReader(open(intl, encoding="utf-8")):
            d = (r.get("_meet_date") or "").strip()
            if d >= WIN_START:
                sig.add("intl:" + (r.get("_meet_name") or "").strip() + ":" + d)
    except Exception:
        pass

sys.stdout.write("\n".join(sorted(sig)) + "\n")
