# ÖVK Qualifikations-Dashboard

Live-Übersicht der österreichischen Athlet:innen, die das Limit für die
**Staatsmeisterschaft 2027 (KDK Classic, Termin folgt)** bereits erreicht haben.
Qualifikationsfenster ab der SM 2026 (05.09.2026). Bis die Limits 2027 veröffentlicht
sind, gelten vorläufig die Limits 2026. Die Ergebnisse der SM 2026 bleiben als Archiv
abrufbar.

Daten stammen aus dem [OpenPowerlifting](https://www.openpowerlifting.org) /
[OpenIPF](https://www.openipf.org) Datensatz (Lizenz: CC0).

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
