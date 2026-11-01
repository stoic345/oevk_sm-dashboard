"""Österreichische Classic-Rekordliste (ÖVK-PDF) -> project-data/oevk_records.csv

Bisher wurde die CSV in Chat-Sitzungen von Hand aus dem PDF erzeugt — nicht
nachvollziehbar und beim nächsten PDF wieder Handarbeit. Dieses Skript liest das PDF über
Wortkoordinaten (pdfplumber), weil der reine Text (pdfminer) die Spalten durcheinanderwirft.

Aufbau einer Rekordseite: pro Block eine Kopfzeile
    "Österr. Rekorde <Disziplin> – <HERREN|DAMEN> – Klasse <-59|+84|…> kg"
und darunter sieben Altersklassenzeilen (Allg./Jug./Jun./AK 1–4). Die Altersklassen-Labels
stehen links und sind gegenüber ihrer Datenzeile um ±2 pt versetzt.
Die Spalten einer Datenzeile werden über das TOKEN-MUSTER zerlegt, nicht über
x-Koordinaten — Herren- und Damenseiten haben verschiedene Spaltenpositionen:
    NAME…  JJ  VEREIN…  kg,d  TT.MM.JJJJ  WETTKAMPF… ORT…
Zeilen ohne kg-Wert ("Kein Limit", "Limit") sind offene Rekorde.

Die Seiten "Bestleistungen BANKDRÜCKEN" (Einzelbewerb) werden übersprungen — dafür gibt es
im Dashboard keine Kategorie.

Aufruf:
    python scripts/parse_records_pdf.py <pdf> <out.csv> [--old <alte.csv>]
Mit --old wird ein Änderungsbericht alt -> neu ausgegeben.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict

import pdfplumber

COLS = ["sex", "age_class", "equipment", "weight_class", "lift",
        "record_kg", "athlete", "meet", "date_iso", "notes", "club"]

LIFTS = {"kniebeugen": "Squat", "bankdrücken": "Bench", "kreuzheben": "Deadlift",
         "kraftdreikampf": "Total"}
SEXES = {"HERREN": "M", "DAMEN": "F"}
AGE_LABELS = {"Allg.:": "Open", "Jug.:": "Jugend", "Jun.:": "Junioren",
              "AK 1:": "AK1", "AK 2:": "AK2", "AK 3:": "AK3", "AK 4:": "AK4"}
AGE_ORDER = ["Jugend", "Junioren", "Open", "AK1", "AK2", "AK3", "AK4"]

KG_RE = re.compile(r"\d+,\d")
DATE_RE = re.compile(r"\d{2}\.\d{2}\.\d{4}")
YEAR_RE = re.compile(r"\d{2}")

HEAD_RE = re.compile(
    r"Österr\. Rekorde (?P<lift>\S+)(?: \(3lift\))? – (?P<sex>HERREN|DAMEN) – "
    r"Klasse (?P<wc>[-+]?\d+\+?) kg")

# Bekannte Fehler im PDF, die bewusst überschrieben werden. Nur anwenden, wenn das PDF
# noch genau den fehlerhaften Wert enthält — sonst ist der Fehler behoben und die Korrektur
# würde einen echten neuen Wert überschreiben.
# (Die frühere Korrektur Herren −59 Kreuzheben Allg. "120,5" ist seit der Liste vom
# 06.09.2026 erledigt — dort steht korrekt 209,5.)
_SULLIVAN_DL = ("PDF (Stand 06.09.2026) nennt für Sullivan, Damen −84 Kreuzheben, 192,5 kg "
                "— das ist ihr Kniebeuge-Wert. Laut SM-Ergebnis (OPL-Meet 2616) war das "
                "Kreuzheben 212,5 kg (3. Versuch gültig), und nur damit stimmt der "
                "Total-Rekord 525 kg derselben Liste (192,5 + 120 + 212,5).")
OVERRIDES = {
    ("F", "Open", "84", "Deadlift"): {"bad": 192.5, "fix": 212.5, "why": _SULLIVAN_DL},
    ("F", "AK1", "84", "Deadlift"): {"bad": 192.5, "fix": 212.5, "why": _SULLIVAN_DL},
}


def _wc(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("+"):
        return raw[1:] + "+"
    return raw.lstrip("-")


def _lines(words, tol=1.6):
    """Wörter zu Zeilen (nach 'top') gruppieren."""
    out: list[list[dict]] = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if out and abs(out[-1][0]["top"] - w["top"]) <= tol:
            out[-1].append(w)
        else:
            out.append([w])
    return [sorted(l, key=lambda w: w["x0"]) for l in out]


def _split_data(tokens: list[str]):
    """NAME… JJ VEREIN… kg,d TT.MM.JJJJ WETTKAMPF/ORT… -> Felder; None = kein Rekord."""
    i_kg = next((i for i, t in enumerate(tokens) if KG_RE.fullmatch(t)), None)
    if i_kg is None:
        return None
    if i_kg + 1 >= len(tokens) or not DATE_RE.fullmatch(tokens[i_kg + 1]):
        raise ValueError(f"kg ohne Datum dahinter: {' '.join(tokens)}")
    i_yr = next((i for i, t in enumerate(tokens[:i_kg]) if YEAR_RE.fullmatch(t)), None)
    if i_yr is None or i_yr == 0:
        raise ValueError(f"kein Jahrgang/Name erkennbar: {' '.join(tokens)}")
    dd, mm, yy = tokens[i_kg + 1].split(".")
    return {
        "athlete": " ".join(tokens[:i_yr]),
        "club": " ".join(tokens[i_yr + 1:i_kg]),
        "record_kg": tokens[i_kg].replace(",", "."),
        "date_iso": f"{yy}-{mm}-{dd}",
        # Wettkampf und Ort wie in der bisherigen CSV einfach hintereinander
        "meet": " ".join(tokens[i_kg + 2:]),
    }


def parse(pdf_path: str) -> list[dict]:
    records: list[dict] = []
    with pdfplumber.open(pdf_path) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            text_head = page.extract_text() or ""
            if "Rekorde -" not in text_head.split("\n", 1)[0]:
                continue                                # Bestleistungen / leere Seite
            words = page.extract_words(x_tolerance=1.5, keep_blank_chars=False)
            # Seitenfuß ("www.kraftdreikampf.at") gehört zu keinem Block.
            words = [w for w in words if "kraftdreikampf.at" not in w["text"]]
            lines = _lines(words)
            # Blockköpfe finden
            heads = []
            for ln in lines:
                txt = " ".join(w["text"] for w in ln)
                m = HEAD_RE.search(txt)
                if m:
                    heads.append((ln[0]["top"], m))
            for i, (top, m) in enumerate(heads):
                bottom = heads[i + 1][0] if i + 1 < len(heads) else page.height
                lift = LIFTS[m["lift"].lower()]
                sex = SEXES[m["sex"]]
                wc = _wc(m["wc"])
                block = [l for l in lines if top + 2 < l[0]["top"] < bottom - 2]
                labels, data = [], []
                for ln in block:
                    # Label über die Tokens erkennen, nicht über eine x-Grenze: auf manchen
                    # Seiten beginnt "Kein Limit" links von der üblichen Namensspalte.
                    lab, dat = None, ln
                    if ln and ln[0]["text"] in ("Allg.:", "Jug.:", "Jun.:"):
                        lab, dat = ln[0]["text"], ln[1:]
                    elif (len(ln) > 1 and ln[0]["text"] == "AK"
                          and re.fullmatch(r"\d:", ln[1]["text"])):
                        lab, dat = f"AK {ln[1]['text']}", ln[2:]
                    if lab:
                        labels.append((ln[0]["top"], lab))
                    if dat:
                        data.append((min(w["top"] for w in dat), dat))
                # Jede Datenzeile dem nächstgelegenen Label zuordnen
                seen = set()
                for dtop, dat in data:
                    best = min(labels, key=lambda l: abs(l[0] - dtop), default=None)
                    if best is None or abs(best[0] - dtop) > 4.5:
                        raise ValueError(f"S.{pno} {sex} {wc} {lift}: Datenzeile ohne "
                                         f"Altersklasse bei top={dtop:.1f}: "
                                         f"{' '.join(w['text'] for w in dat)}")
                    ac = AGE_LABELS.get(best[1])
                    if ac is None:
                        raise ValueError(f"S.{pno}: unbekanntes Label {best[1]!r}")
                    if ac in seen:
                        raise ValueError(f"S.{pno} {sex} {wc} {lift}: {ac} doppelt")
                    seen.add(ac)
                    rec = {"sex": sex, "age_class": ac, "equipment": "Raw",
                           "weight_class": wc, "lift": lift, "record_kg": "",
                           "athlete": "", "meet": "", "date_iso": "", "notes": "",
                           "club": ""}
                    try:
                        fields = _split_data([w["text"] for w in dat])
                    except ValueError as exc:
                        raise ValueError(f"S.{pno} {sex} {wc} {lift} {ac}: {exc}") from None
                    if fields is None:
                        # "Kein Limit" / "Limit": kein Rekord eingetragen
                        rec["notes"] = "Rekord offen"
                    else:
                        rec.update(fields)
                    records.append(rec)
                # Labels ohne Datenzeile = offene Rekorde ohne Text (kommt vor)
                for _, lab in labels:
                    ac = AGE_LABELS.get(lab)
                    if ac and ac not in seen:
                        records.append({"sex": sex, "age_class": ac, "equipment": "Raw",
                                        "weight_class": wc, "lift": lift, "record_kg": "",
                                        "athlete": "", "meet": "", "date_iso": "",
                                        "notes": "Rekord offen", "club": ""})
                        seen.add(ac)
    return records


def _key(r):
    return (r["sex"], r["age_class"], r["weight_class"], r["lift"])


def apply_overrides(records):
    applied = []
    for r in records:
        ov = OVERRIDES.get(_key(r))
        if not ov or not r["record_kg"] or abs(float(r["record_kg"]) - ov["bad"]) >= 0.01:
            continue
        r["record_kg"] = f'{ov["fix"]:g}'
        r["notes"] = "korrigiert: " + ov["why"]
        applied.append((_key(r), ov["bad"], float(r["record_kg"])))
    return applied


# Seit Jahren unverändert in der offiziellen Liste und KEIN Parserfehler: Damen −47 Total
# AK 1/2 = 297,5 (Schwengl-Forsthuber, EM 2015) über Allg. = 292,5. Nach Wettkampfordnung
# §08 zählt eine Rekordleistung nur in der Altersklasse der jeweiligen Meisterschaft — ein
# AK-Ergebnis wird nicht automatisch zum Allgemein-Rekord. Nicht "korrigieren".
KNOWN_EXCEPTIONS = {("F", "47", "Total")}


def check_open_is_max(records):
    """Plausibilitätsprüfung: liegt ein Altersklassen-Rekord über dem Allgemein-Rekord
    derselben Gewichtsklasse/Disziplin? Bei Ergebnissen aus Allgemein-Meisterschaften
    (z. B. Staatsmeisterschaft Allg) ist das ein Fehler in der Liste. Klassen ohne
    Allg.-Zeile (−43 / −53, nur Nachwuchs) werden übersprungen."""
    by = {}
    for r in records:
        if r["record_kg"]:
            by.setdefault((r["sex"], r["weight_class"], r["lift"]), {})[r["age_class"]] = r
    bad = []
    for k, acs in by.items():
        op = acs.get("Open")
        if op is None or k in KNOWN_EXCEPTIONS:
            continue
        for ac, r in acs.items():
            if ac != "Open" and float(r["record_kg"]) > float(op["record_kg"]) + 1e-9:
                bad.append((k, ac, r["record_kg"], op["record_kg"]))
    return bad


def _fmt(v: str) -> str:
    """'175.0' -> '175' wie in der bisherigen CSV."""
    if not v:
        return ""
    f = float(v)
    return f"{f:g}"


def write(records, out_path):
    lift_order = {"Squat": 0, "Bench": 1, "Deadlift": 2, "Total": 3}
    def wc_key(w):
        return (float(w.rstrip("+")), w.endswith("+"))
    records.sort(key=lambda r: (0 if r["sex"] == "M" else 1, lift_order[r["lift"]],
                                wc_key(r["weight_class"]), AGE_ORDER.index(r["age_class"])))
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for r in records:
            w.writerow({**r, "record_kg": _fmt(r["record_kg"])})


def report(records, old_path):
    key = lambda r: (r["sex"], r["age_class"], r["weight_class"], r["lift"])
    with open(old_path, encoding="utf-8") as fh:
        old = {key(r): r for r in csv.DictReader(fh)}
    new = {key(r): r for r in records}
    print(f"\nalt: {len(old)} Einträge · neu: {len(new)} Einträge")
    only_old, only_new = sorted(set(old) - set(new)), sorted(set(new) - set(old))
    print(f"nur alt: {len(only_old)} · nur neu: {len(only_new)}")
    for k in only_old:
        print("  NUR ALT", k)
    for k in only_new:
        print("  NUR NEU", k, new[k]["record_kg"], new[k]["athlete"])
    changed, lower = [], []
    for k in sorted(set(old) & set(new)):
        o, n = old[k], new[k]
        ov = float(o["record_kg"]) if o["record_kg"] else None
        nv = float(n["record_kg"]) if n["record_kg"] else None
        if ov != nv or (o["athlete"] != n["athlete"] and nv is not None):
            changed.append((k, o, n))
            if ov is not None and (nv is None or nv < ov):
                lower.append((k, ov, nv))
    print(f"geändert: {len(changed)}")
    for k, o, n in changed:
        print(f"  {k[0]} {k[3]:8} {k[2]:>4} {k[1]:8}  "
              f"{o['record_kg'] or '—':>6} {o['athlete'][:24]:24} -> "
              f"{_fmt(n['record_kg']) or '—':>6} {n['athlete'][:24]:24} {n['date_iso']}")
    print(f"GESUNKEN/entfernt (einzeln prüfen!): {len(lower)}")
    for k, ov, nv in lower:
        print("  ", k, ov, "->", nv)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out")
    ap.add_argument("--old")
    a = ap.parse_args()
    recs = parse(a.pdf)
    applied = apply_overrides(recs)
    for key, bad, good in applied:
        print(f"Korrektur angewendet: {key}: {bad} -> {good}")
    missing = [k for k in OVERRIDES if k not in {x[0] for x in applied}]
    for k in missing:
        print(f"Korrektur NICHT angewendet (PDF-Wert ist nicht mehr der Fehlwert): {k}")
    viol = check_open_is_max(recs)
    print(f"Konsistenz Allg. >= alle Altersklassen: {len(viol)} Verstoesse")
    for k, ac, v, op in viol:
        print(f"  VERSTOSS {k}: {ac} {v} > Allg. {op}")
    if a.old:
        report(recs, a.old)
    write(recs, a.out)
    print(f"\n{len(recs)} Einträge -> {a.out}")


if __name__ == "__main__":
    sys.exit(main())
