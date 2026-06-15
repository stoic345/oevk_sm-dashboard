# ÖVK Qualifikations-Dashboard

Live-Übersicht der österreichischen Athlet:innen, die das Limit für die
**Staatsmeisterschaft 2026 (KDK Classic, 5.–6. September 2026)** bereits erreicht
haben.

Daten stammen aus dem [OpenPowerlifting](https://www.openpowerlifting.org) /
[OpenIPF](https://www.openipf.org) Datensatz (Lizenz: CC0).

> ⚠ **Beta:** Diese Seite befindet sich in Entwicklung. Berechnungen können
> fehlerhaft sein — bitte im Zweifel auf openpowerlifting.org gegenprüfen.

---

## Lokal starten

```bash
pip install -r requirements.txt
streamlit run my_analysis/oevk_dashboard.py
```

Voraussetzung: Python ≥ 3.10.

## Datenstand aktualisieren

```bash
python scripts/check_updates.py
```

Skript zieht den neuesten Stand von OpenPowerlifting (falls dieses Repo ein Fork
von `openpowerlifting/opl-data` ist) und touched die `.last_check`-Marker-Datei,
die das Dashboard für die „Zuletzt geprüft"-Anzeige liest.

## Deploy

Auf [Streamlit Community Cloud](https://share.streamlit.io) deployt — Main-File:
`my_analysis/oevk_dashboard.py`.

## Lizenz / Quellen

- Datensatz: OpenPowerlifting Project — CC0
- Code: MIT

## Kontakt

Bei Fragen oder Fehlerberichten:
[Issue eröffnen](../../issues).
