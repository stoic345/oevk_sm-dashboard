# DATA_VERSION: 2026-07-23
# ^ Auto-bumped by the sync-oevk-data GitHub Action whenever meet data changes.
#   Touching this source file forces Streamlit Community Cloud to redeploy with a
#   fresh checkout — data-only commits alone do NOT trigger a redeploy, so new
#   meets would otherwise stay invisible on the live app until a manual reboot.
import streamlit as st
import streamlit.components.v1 as _components
import pandas as pd
import numpy as np
import base64
import html as _html
import re
from pathlib import Path
from urllib.parse import quote as _urlquote
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- ASSETS ---
ASSETS_DIR = Path(__file__).parent / "assets"
PROJECT_DATA_DIR = Path(__file__).parent.parent / "project-data"


def logo_html(max_height_px: int = 56) -> str:
    """Lädt das ÖVK-Logo und liefert es als <img> mit data: URI.
    Sucht zuerst in project-data/, dann in my_analysis/assets/. Fallback: Emoji."""
    candidates = [
        PROJECT_DATA_DIR / "oevklogo.png",
        PROJECT_DATA_DIR / "oevk_logo.png",
        ASSETS_DIR / "oevk_logo.png",
        ASSETS_DIR / "oevk_logo.jpg",
        ASSETS_DIR / "oevk_logo.svg",
        ASSETS_DIR / "logo.png",
    ]
    for p in candidates:
        if not p.exists():
            continue
        try:
            ext = p.suffix.lower()
            mime = "image/svg+xml" if ext == ".svg" else (
                "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
            )
            b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            return (
                f'<img src="data:{mime};base64,{b64}" alt="ÖVK" '
                f'style="height:{max_height_px}px;width:auto;display:block">'
            )
        except OSError:
            continue
    return '<span style="font-size:30px">🏋️</span>'

# --- DESIGN SYSTEM (übernommen aus dem Claude-Design-Handoff) ---
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
  --bg:#0B0B0C; --bg-elev:#121214; --surface:#18181B; --surface-2:#1F1F23; --surface-3:#26262B;
  --line:#2A2A30; --line-soft:#202024;
  --gold:#C9AE5B; --gold-bright:#E2C977; --gold-dim:#8C7A3E; --gold-ink:#1A1606;
  --text:#F5F5F4; --text-2:#B6B6BB; --text-3:#76767D;
  --green:#4FB477; --green-bright:#7BD79C; --green-bg:rgba(34,84,52,0.32);
  --green-bg-soft:rgba(34,84,52,0.16); --green-line:rgba(79,180,119,0.40);
  --amber:#D9A441; --red:#C95F5F;
  --font-body:"Archivo",system-ui,sans-serif;
  --font-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  --r-sm:6px; --r-md:10px; --r-lg:14px; --r-xl:18px;
}

/* Streamlit chrome — Header + Toolbar bleiben sichtbar (Toolbar enthält den Sidebar-Expand-Button!).
   Nur die Menü-/Status-/Deploy-Elemente entfernen, NICHT die ganze Toolbar. */
#MainMenu, footer {visibility:hidden; height:0;}
header[data-testid="stHeader"] { background:transparent !important; }
header[data-testid="stHeader"] [data-testid="stMainMenu"],
header[data-testid="stHeader"] [data-testid="stStatusWidget"],
header[data-testid="stHeader"] [data-testid="stAppDeployButton"],
header[data-testid="stHeader"] [data-testid="stToolbarActions"] { display:none !important; }
.stApp {
  background:
    radial-gradient(1200px 480px at 18% -10%, rgba(201,174,91,0.06), transparent 60%),
    var(--bg);
  color: var(--text);
  font-family: var(--font-body);
}
.block-container { max-width:100%; padding-top:1.2rem; padding-bottom:4rem; padding-left:2.5rem; padding-right:2.5rem; }

/* Sidebar */
[data-testid="stSidebar"] { background:var(--surface); border-right:1px solid var(--line); }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { font-family:var(--font-body); }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMultiSelect label, [data-testid="stSidebar"] .stDateInput label {
  font-family:var(--font-mono) !important; font-size:10.5px !important; letter-spacing:0.14em !important;
  text-transform:uppercase !important; color:var(--text-2) !important;
}
[data-baseweb="tag"] { background:rgba(201,174,91,0.16) !important; color:var(--gold-bright) !important;
  border:1px solid var(--gold-dim) !important; }
[data-baseweb="tag"] span { color:var(--gold-bright) !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background:var(--bg-elev) !important;
  border:1px solid var(--gold-dim) !important; border-radius:8px !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover { border-color:var(--gold) !important; }
[data-testid="stSidebar"] [data-baseweb="select"] input {
  background:transparent !important; border:none !important;
  box-shadow:none !important; color:#FFFFFF !important; }
/* Selected value + placeholder fully white (Baseweb default 60 % opacity = grau) */
[data-testid="stSidebar"] [data-baseweb="select"] > div div,
[data-testid="stSidebar"] [data-baseweb="select"] input {
  color:#FFFFFF !important; opacity:1 !important; }
/* "X" + Dropdown-Pfeil weiß */
[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="icon"],
[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="icon"] svg,
[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="icon"] path {
  color:#FFFFFF !important; fill:#FFFFFF !important; opacity:1 !important; }

/* Kicker / eyebrow */
.kicker { font-family:var(--font-mono); font-size:11px; letter-spacing:0.18em; text-transform:uppercase; color:var(--text-3); font-weight:500; }
.kicker--gold { color:var(--gold); }
.mono { font-family:var(--font-mono); font-variant-numeric:tabular-nums; }

/* Top header */
.topbar { display:flex; align-items:center; justify-content:center; gap:20px;
  padding:6px 22px; margin-bottom:22px; border:1px solid var(--line); border-radius:var(--r-lg);
  background:linear-gradient(180deg, var(--surface), var(--bg-elev)); overflow:hidden; }
.hero { margin:6px 0 18px; }
.hero__title { font-family:var(--font-display); font-size:34px; font-weight:800;
  letter-spacing:-0.01em; color:var(--text); line-height:1.1; }
.hero__title::after { content:""; display:block; width:54px; height:3px; margin-top:8px;
  background:linear-gradient(90deg, var(--gold), var(--gold-dim)); border-radius:2px; }
.hero__sub { font-family:var(--font-mono); font-size:13px; color:var(--text-2);
  letter-spacing:0.02em; margin-top:10px; max-width:none; white-space:nowrap;
  overflow:hidden; text-overflow:ellipsis; }
/* Data-Freshness-Status-Pills (Datenstand, letzte Aktualisierung, Quelle) */
.data-status { display:grid; grid-template-columns:repeat(4, 1fr); gap:16px;
  margin:0; align-items:stretch; }
@media (max-width:900px) { .data-status { grid-template-columns:1fr 1fr; } }
.status-pill { display:flex; align-items:center; justify-content:center; gap:8px;
  background:var(--bg-elev); border:1px solid var(--gold-dim); border-radius:var(--r-sm);
  padding:6px 12px; font-family:var(--font-mono); font-size:11.5px; line-height:1.15;
  min-width:0; text-align:center; }
.status-pill .lab, .status-pill .val { text-align:center; }
.status-pill .lab { color:var(--gold); letter-spacing:0.14em; text-transform:uppercase;
  font-weight:600; font-size:10px; }
.status-pill .val { color:var(--text); font-weight:600; font-variant-numeric:tabular-nums; }
.status-pill a, .status-pill a:link, .status-pill a:visited {
  color:var(--gold-bright) !important; text-decoration:none !important; font-weight:600 !important;
}
.status-pill a:hover { color:var(--text) !important; text-decoration:underline !important; }
.status-pill.is-stale { border-color:var(--amber); }
.status-pill.is-stale .val { color:var(--amber); }
.status-pill .dot { width:8px; height:8px; border-radius:50%; background:var(--green); display:inline-block; }
.status-pill.is-stale .dot { background:var(--amber); }
.brand { display:flex; align-items:center; gap:16px; min-width:0; margin-right:auto; }
a.brand.brand--link, a.brand.brand--link:link, a.brand.brand--link:visited,
a.brand.brand--link:hover, a.brand.brand--link:active {
  text-decoration:none !important; color:inherit !important;
}
a.brand.brand--link { cursor:pointer; transition:opacity .14s ease; }
a.brand.brand--link:hover { opacity:0.85; }
.logo { width:46px; height:46px; flex:none; border-radius:11px; display:grid; place-items:center;
  background:linear-gradient(150deg,#1d1d20,#121214); border:1px solid var(--gold-dim);
  font-size:24px; }
.logo--img { width:auto; height:auto; min-width:0; padding:0;
  background:transparent; border:none; border-radius:0;
  box-shadow:none; line-height:0; }
.logo--img img { display:block; height:130px; width:auto;
  border:none; border-radius:0; box-shadow:none; background:transparent;
  transition:opacity .14s ease; }
.logo--img:hover img { opacity:0.85; }
.brand__divider { width:1px; align-self:stretch; background:var(--line); margin:0 4px; }
.brand__title { font-family:var(--font-display); font-weight:800; font-size:30px; letter-spacing:-0.01em;
  line-height:1.15; text-transform:none; color:var(--text); }
.brand__title .beta { display:inline-block; vertical-align:middle; font-family:var(--font-mono);
  font-size:11px; font-weight:700; letter-spacing:0.16em; color:var(--amber);
  border:1px solid var(--amber); border-radius:4px; padding:2px 7px; margin-left:10px;
  background:rgba(217,164,65,0.10); }
/* Beta-Warning-Banner unter der Topbar */
.dev-banner { display:flex; align-items:center; justify-content:center; gap:10px;
  background:rgba(217,164,65,0.10); border:1px solid rgba(217,164,65,0.45);
  border-left:3px solid var(--amber); border-radius:var(--r-sm);
  padding:10px 16px; margin:0;
  font-family:var(--font-mono); font-size:12px; color:var(--text);
  letter-spacing:0.02em; text-align:center; }
.dev-banner .ic { color:var(--amber); font-size:16px; line-height:1; }
.dev-banner b { color:var(--amber); font-weight:700; }
.brand__title .accent { color:var(--gold-bright); }
.brand__date { font-family:var(--font-mono); font-size:14px; letter-spacing:0.14em;
  text-transform:uppercase; color:var(--gold); font-weight:600; margin-top:4px; }
.brand__sub { font-family:var(--font-body); font-size:17px; letter-spacing:0.005em; color:var(--text);
  text-transform:none; margin-top:8px; font-weight:400; line-height:1.4; }
.target { display:flex; align-items:stretch; gap:18px; padding:14px 20px 14px 18px;
  border:1px solid var(--line); border-left:3px solid var(--gold); border-radius:var(--r-md);
  background:linear-gradient(180deg, var(--surface), var(--bg-elev));
  box-shadow:0 0 0 1px rgba(201,174,91,0.06); min-width:360px; }
.target__body { display:flex; flex-direction:column; justify-content:center; gap:3px; }
.target .k { font-family:var(--font-mono); font-size:10px; letter-spacing:0.18em; color:var(--gold); text-transform:uppercase; font-weight:500; }
.target .v { font-family:var(--font-body); font-weight:700; font-size:17px; color:var(--text); line-height:1.2; letter-spacing:-0.005em; }
.target .v2 { font-family:var(--font-mono); font-size:12.5px; color:var(--gold-bright); letter-spacing:0.02em; margin-top:2px; font-weight:500; }
.target__count { display:flex; flex-direction:column; align-items:center; justify-content:center;
  padding-left:18px; border-left:1px solid var(--line); min-width:68px; }
.target__count .num { font-family:var(--font-mono); font-size:48px; font-weight:700; color:var(--gold-bright); line-height:1; }
.target__count .unit { font-family:var(--font-mono); font-size:11px; letter-spacing:0.14em; color:var(--gold); text-transform:uppercase; margin-top:5px; font-weight:600; white-space:nowrap; }
.target--solo { padding:10px 18px; min-width:0; }
.target--solo .target__count { padding-left:0; border-left:none; }

/* KPI cards */
.kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:0 0 18px; }
.kpis--3 { grid-template-columns:repeat(3,1fr); }
@media (max-width:760px) { .kpis--3 { grid-template-columns:1fr; } }

/* Credit-Footer */
.credit {
  margin-top:32px; padding:18px 0; text-align:center;
  font-family:var(--font-mono); font-size:11px; color:var(--text-3);
  border-top:1px solid var(--line); letter-spacing:0.06em;
}
.credit a { color:var(--gold); text-decoration:none; }
.credit a:hover { color:var(--gold-bright); text-decoration:underline; }
.kpi { position:relative; overflow:hidden; background:linear-gradient(180deg,var(--surface),var(--bg-elev));
  border:1px solid var(--line); border-radius:var(--r-lg); padding:20px; display:flex; flex-direction:column; gap:12px; }
.kpi::after { content:""; position:absolute; inset:0 0 auto 0; height:2px;
  background:linear-gradient(90deg,transparent,var(--gold-dim),transparent); opacity:.5; }
.kpi { text-align:center; }
.kpi__top { display:flex; align-items:center; justify-content:center; }
.kpi__value { display:block; text-align:center; }
.kpi__foot { text-align:center; margin-top:6px; }
.kpi__icon { width:34px; height:34px; border-radius:9px; display:grid; place-items:center; font-size:17px;
  background:rgba(201,174,91,0.10); border:1px solid var(--gold-dim); }
.kpi__label { font-family:var(--font-mono); font-size:14px; letter-spacing:0.14em; text-transform:uppercase; color:var(--gold-bright); font-weight:600; margin-bottom:10px; display:block; }
.kpi__value { font-family:var(--font-mono); font-size:36px; font-weight:600; line-height:1; letter-spacing:-0.01em; color:var(--text); }
.kpi--accent .kpi__value { color:var(--text); }
.kpi__foot { font-family:var(--font-mono); font-size:11px; color:var(--text-3); }
.kpi__foot .up { color:var(--green); }

/* Section heading */
.section-head { display:flex; align-items:center; justify-content:space-between; gap:16px; margin:0; }
.section-head h2 { font-family:var(--font-body); font-size:21px; font-weight:700; letter-spacing:-0.01em; margin:0; }
.section-head .meta { font-family:var(--font-mono); font-size:12px; color:var(--gold); font-weight:600; }
/* CSV-Export-Button (Hauptbereich, neben dem Tabellen-Header) */
[data-testid="stDownloadButton"] > button {
  background:var(--surface) !important; border:1px solid var(--gold-dim) !important;
  border-radius:var(--r-sm) !important; color:var(--gold-bright) !important;
  font-family:var(--font-mono) !important; font-size:11px !important; font-weight:600 !important;
  letter-spacing:0.08em !important; text-transform:uppercase !important; box-shadow:none !important;
  transition:background .14s ease, color .14s ease, border-color .14s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
  background:var(--gold) !important; border-color:var(--gold-bright) !important; color:#0B0B0C !important;
}
[data-testid="stDownloadButton"] > button p { color:inherit !important; margin:0 !important; }

/* Pills */
.pill { display:inline-flex; align-items:center; gap:5px; font-family:var(--font-mono); font-size:10.5px;
  letter-spacing:0.08em; text-transform:uppercase; font-weight:500; padding:4px 9px; border-radius:999px; white-space:nowrap; }
.pill--q { background:var(--green-bg); color:var(--green-bright); border:1px solid var(--green-line); }
.pill--n { background:var(--surface-2); color:var(--text-3); border:1px solid var(--line); }

/* Progress-to-limit */
.prog { display:flex; flex-direction:column; gap:4px; min-width:120px; }
.prog__track { height:7px; border-radius:4px; background:var(--surface-2); overflow:hidden; position:relative; }
.prog__track::after { content:""; position:absolute; top:-2px; bottom:-2px; left:78%; width:2px; background:var(--text); opacity:.45; }
.prog__fill { height:100%; border-radius:4px; }
.prog__fill--q { background:linear-gradient(90deg,var(--green),var(--green-bright)); }
.prog__fill--n { background:linear-gradient(90deg,var(--gold-dim),var(--amber)); }
.prog__meta { display:flex; justify-content:space-between; font-family:var(--font-mono); font-size:10px; color:var(--text-3); }

/* signed diff */
.diff { font-family:var(--font-mono); font-weight:600; font-variant-numeric:tabular-nums; }
.diff--pos { color:var(--green-bright); }
.diff--neg { color:var(--amber); }
.diff--far { color:var(--red); }

/* Tables */
.tablecard { background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg); overflow:hidden; margin-bottom:26px; }
.tablescroll { overflow-x:auto; }
table.tbl { width:100%; border-collapse:collapse; font-size:13px; }
table.tbl thead th { background:var(--surface-2); font-family:var(--font-mono); font-size:12px; letter-spacing:0.12em;
  text-transform:uppercase; color:var(--gold-bright); font-weight:700; text-align:center; padding:14px 14px;
  border-bottom:2px solid var(--gold-dim); white-space:nowrap; }
table.tbl thead th.num, table.tbl tbody td.num { text-align:center; font-variant-numeric:tabular-nums; }
table.tbl tbody td.l { text-align:left; }
table.tbl thead th .u { text-transform:lowercase; font-weight:500; opacity:0.85; margin-left:4px; }
table.tbl thead th.sortable { cursor:pointer; user-select:none; transition:color .12s ease; }
table.tbl thead th.sortable:hover { color:#fff !important; }
table.tbl thead th .sort-arrow { font-size:10px; opacity:0.45; margin-left:5px; transition:opacity .12s ease; }
table.tbl thead th.sortable:hover .sort-arrow { opacity:0.9; }
table.tbl thead th.sort-active { color:#fff !important; }
table.tbl thead th.sort-active .sort-arrow { opacity:1; color:var(--gold-bright); }
table.tbl thead th.nosort { cursor:default; }
table.tbl thead tr.grp th { background:transparent; border-bottom:none; padding:6px 14px 2px;
  color:var(--text-3); text-transform:none; letter-spacing:0; font-weight:500; }
table.tbl thead tr.grp th.grp-kg { border-bottom:1px solid var(--gold-dim);
  color:var(--gold-bright); text-align:center; font-family:var(--font-mono); }
a.nm-link, a.nm-link:link, a.nm-link:visited, a.nm-link:hover, a.nm-link:active {
  text-decoration:none !important;
}
a.nm-link { color:var(--text) !important; cursor:pointer; }
a.nm-link:hover { color:var(--gold-bright) !important; }
.profile-card { background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg);
  padding:20px 22px; margin-top:20px; box-shadow:var(--shadow-md); }
.profile-head { display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom:14px; }
.profile-name { font-family:var(--font-display); font-size:24px; font-weight:700; color:var(--text); margin:0; }
.profile-sub { font-family:var(--font-mono); font-size:12px; color:var(--text-3); margin-top:4px; letter-spacing:0.08em; }
.profile-stats { display:flex; gap:14px; flex-wrap:wrap; margin:6px 0 18px; }
.profile-stat { background:var(--bg-elev); border:1px solid var(--line); border-radius:var(--r-sm);
  padding:8px 14px; min-width:120px; }
.profile-stat .lab { font-family:var(--font-mono); font-size:10px; letter-spacing:0.14em;
  text-transform:uppercase; color:var(--text-3); }
.profile-stat .val { font-family:var(--font-mono); font-weight:600; font-size:18px; color:var(--gold-bright);
  font-variant-numeric:tabular-nums; }
.profile-close { font-family:var(--font-mono); font-size:11px; letter-spacing:0.12em; text-transform:uppercase;
  color:var(--text-3); border:1px solid var(--line); border-radius:var(--r-sm); padding:6px 10px;
  text-decoration:none; white-space:nowrap; }
.profile-close:hover { color:var(--gold-bright); border-color:var(--gold-dim); }
.profile-note { font-family:var(--font-mono); font-size:10px; color:var(--text-3); margin-top:10px; opacity:0.8; }
/* Streamlit Cloud "View source on GitHub"-Badge verstecken.
   WICHTIG: NIEMALS stHeader oder stToolbar komplett verstecken — die Toolbar enthält den
   Sidebar-Expand-Button (»). Nur die Badge-/Menü-/Deploy-Elemente entfernen. */
[data-testid="stDecoration"],
[data-testid="stToolbarActions"],
[data-testid="stAppDeployButton"],
.viewerBadge_container__1QSob,
.viewerBadge_container__r5tak,
.viewerBadge_link__1S137,
.viewerBadge_link__qRIco,
.viewerBadge_text__1JaDK,
a[href*="streamlit.io"]:has(> img),
a[href*="github.com"][title*="View source"],
#MainMenu,
footer { display: none !important; visibility: hidden !important; }
/* Unused space above the header — Streamlit's default block top-padding minimieren */
[data-testid="stMain"] .block-container,
.block-container,
[data-testid="stAppViewBlockContainer"] {
  padding-top: 0.6rem !important;
}
[data-testid="stMain"] [data-testid="stVerticalBlock"] {
  gap: 12px !important;
}
/* st.markdown-Wrapper um eingebettete Style-Tags visuell unsichtbar machen
   (verhindert Vertical Jump bei conditional CSS-Injection). */
[data-testid="stMarkdown"]:has(> [data-testid="stMarkdownContainer"] > style:only-child),
[data-testid="stMarkdown"]:has(style:only-child) {
  margin:0 !important; padding:0 !important; min-height:0 !important; height:0 !important;
  display:none !important;
}
/* Tabellen-Karte über Stacking-Context sauber halten */
.tablecard { position:relative; z-index:0; }

/* === Sidebar Fold: Streamlits NATIVE Collapse nutzen ===
   Keine Breiten-Sperre, kein transform:none — sonst kann Streamlit nicht einklappen.
   Wichtig: Collapse-Button = <div data-testid><button>; Expand-Button = <button data-testid>.
   Daher beide DOM-Strukturen abdecken. */
/* Position (ortsfest oben links) — am äußersten Element */
[data-testid="stSidebarCollapseButton"],
button[data-testid="stExpandSidebarButton"] {
  position:fixed !important; top:12px !important; left:12px !important; z-index:1000000 !important;
  opacity:1 !important; visibility:visible !important;
}
/* Gold-Kreis-Optik — am tatsächlichen Button-Element beider Strukturen */
[data-testid="stSidebarCollapseButton"] button,
button[data-testid="stExpandSidebarButton"] {
  width:42px !important; height:42px !important; min-width:42px !important; padding:0 !important; margin:0 !important;
  display:flex !important; align-items:center !important; justify-content:center !important;
  background:linear-gradient(180deg, var(--gold-bright) 0%, var(--gold) 100%) !important;
  border:1px solid var(--gold-bright) !important; border-radius:50% !important;
  box-shadow:0 4px 14px rgba(201,174,91,0.45), inset 0 1px 0 rgba(255,255,255,0.35) !important;
  transition:transform .15s ease, filter .15s ease, box-shadow .15s ease !important;
  opacity:1 !important; visibility:visible !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
button[data-testid="stExpandSidebarButton"]:hover {
  filter:brightness(1.08) !important; transform:scale(1.06) !important;
  box-shadow:0 6px 22px rgba(201,174,91,0.6), inset 0 1px 0 rgba(255,255,255,0.45) !important;
}
[data-testid="stSidebarCollapseButton"] button:active,
button[data-testid="stExpandSidebarButton"]:active { transform:scale(0.96) !important; }
/* Icon (SVG oder Material-Span) dunkel einfärben für Kontrast auf Gold */
[data-testid="stSidebarCollapseButton"] button *,
button[data-testid="stExpandSidebarButton"] * {
  color:#0B0B0C !important; fill:#0B0B0C !important; -webkit-text-fill-color:#0B0B0C !important;
}
/* Platz für den fixierten Button schaffen, damit er das "VEREIN"-Label nicht überdeckt */
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding-top:44px !important; }
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] { min-height:0 !important; }
/* Sidebar Header: FILTER-Kicker + Live-Scope-Counter */
.sb-kicker { font-family:var(--font-mono); font-size:11px; letter-spacing:0.22em;
  text-transform:uppercase; color:var(--gold-bright); font-weight:700;
  text-align:center; margin:4px 0 8px;
  padding-bottom:10px; position:relative; }
.sb-kicker::after { content:""; position:absolute; left:25%; right:25%; bottom:0; height:1px;
  background:linear-gradient(90deg, transparent, var(--gold-dim) 50%, transparent);
  opacity:0.6; }
.sb-scope { font-family:var(--font-mono); font-size:11px; color:var(--text-2);
  letter-spacing:0.04em; text-align:center; margin:10px 0 6px; line-height:1.6; }
.sb-scope__big { color:var(--gold-bright); font-weight:700; font-size:14px;
  font-variant-numeric:tabular-nums; margin-right:2px; }
.sb-scope__sep { color:var(--text-3); margin:0 2px; opacity:0.5; }
/* Goldlinien-Trenner in der Sidebar */
.sb-divider { height:1px; background:linear-gradient(90deg, transparent 0%, var(--gold) 50%, transparent 100%);
  margin:14px 2px; opacity:0.55; }
/* SM-Limits Karte in der Sidebar */
.lim-card { background:var(--bg-elev); border:1px solid var(--gold-dim); border-radius:var(--r-md);
  padding:14px 14px 12px; width:100%; box-sizing:border-box; margin:0; }
/* Sidebar: Checkbox + Limits-Card auf exakt gleiche Breite zwingen */
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has([data-testid="stCheckbox"]),
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.lim-card) {
  padding-left:0 !important; padding-right:0 !important;
  margin-left:0 !important; margin-right:0 !important;
  width:100% !important;
}
.lim-head { font-family:var(--font-mono); font-size:11px; letter-spacing:0.18em; text-transform:uppercase;
  color:var(--gold-bright); font-weight:700; text-align:center; margin-bottom:10px;
  padding-bottom:8px; border-bottom:1px solid var(--line); }
.lim-cap { font-family:var(--font-mono); font-size:10.5px; letter-spacing:0.16em; text-transform:uppercase;
  color:var(--gold-bright); font-weight:600; margin:8px 0 4px; text-align:center; }
.lim-tbl { width:100%; border-collapse:collapse; font-family:var(--font-mono); font-size:12px;
  font-variant-numeric:tabular-nums; }
.lim-tbl td { padding:4px 6px; border-bottom:1px solid var(--line-soft); }
.lim-tbl tr:last-child td { border-bottom:none; }
.lim-wc { color:var(--text); width:55%; }
.lim-val { color:var(--gold); text-align:right; font-weight:600; }
.lim-foot { margin-top:10px; padding-top:8px; border-top:1px solid var(--line);
  font-family:var(--font-mono); font-size:9.5px; letter-spacing:0.1em; text-transform:uppercase;
  color:var(--text-3); text-align:center; }
/* Selectbox-Labels in der Sidebar (Verein, Athlet:in, Gewichtsklasse, Wettkampf) — zentriert + größer */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > label,
[data-testid="stSidebar"] [data-testid="stSelectbox"] label,
[data-testid="stSidebar"] [data-testid="stSelectbox"] label > div,
[data-testid="stSidebar"] [data-testid="stSelectbox"] label p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] > div,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
  text-align:center !important; justify-content:center !important;
  display:flex !important; width:100% !important;
  font-size:14px !important; font-weight:600 !important;
  letter-spacing:0.10em !important; color:var(--gold-bright) !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] label > div { display:block !important; }
/* Reset-Button "Filter zurücksetzen" — kompakte Goldpille, mittig */
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has([data-testid="stButton"]),
[data-testid="stSidebar"] [data-testid="stButton"] {
  display:flex !important; justify-content:center !important; width:100% !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button {
  background:var(--surface) !important; border:1px solid var(--gold-dim) !important;
  border-radius:var(--r-sm) !important; color:var(--text) !important;
  font-family:var(--font-mono) !important; font-size:9.5px !important; font-weight:600 !important;
  letter-spacing:0.10em !important; text-transform:uppercase !important;
  padding:5px 12px !important; margin:8px auto 2px !important; min-height:0 !important;
  line-height:1.2 !important; width:auto !important;
  transition:background .14s ease, border-color .14s ease, color .14s ease !important;
  box-shadow:none !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
  background:var(--gold) !important; border-color:var(--gold-bright) !important; color:#0B0B0C !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:focus,
[data-testid="stSidebar"] [data-testid="stButton"] > button:active {
  background:var(--surface) !important; border-color:var(--gold-bright) !important;
  color:var(--gold-bright) !important; box-shadow:none !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button p,
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover p {
  color:inherit !important; margin:0 !important; font-size:9.5px !important;
}
/* Selectboxen — ALLE Text- und Placeholder-Knoten auf Weiß setzen.
   Aggressives Targeting: jede Span/P/Div/Input innerhalb der Selectbox. */
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] p,
[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="select"] input,
[data-testid="stSidebar"] [data-baseweb="select"] [class*="placeholder"],
[data-testid="stSidebar"] [data-baseweb="select"] [class*="Placeholder"],
[data-testid="stSidebar"] div[role="combobox"],
[data-testid="stSidebar"] div[role="combobox"] * {
  color: var(--text) !important; opacity: 1 !important;
  -webkit-text-fill-color: var(--text) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] input::placeholder,
[data-testid="stSidebar"] [data-baseweb="select"] input::-webkit-input-placeholder,
[data-testid="stSidebar"] [data-baseweb="select"] input::-moz-placeholder {
  color: var(--text) !important; opacity: 1 !important; -webkit-text-fill-color: var(--text) !important;
}

/* X-Button (Clear) — IMMER sichtbar in der Icon-Spalte (2. Kind des combobox).
   BaseWeb versteckt ihn standardmäßig bis Hover — wir zwingen ihn permanent sichtbar. */
[data-testid="stSidebar"] div[role="combobox"] > div:last-child {
  opacity: 1 !important; visibility: visible !important;
}
[data-testid="stSidebar"] div[role="combobox"] > div:last-child [role="button"],
[data-testid="stSidebar"] div[role="combobox"] > div:last-child button,
[data-testid="stSidebar"] div[role="combobox"] > div:last-child > div {
  opacity: 1 !important; visibility: visible !important; display: inline-flex !important;
  pointer-events: auto !important;
}
/* ALLE SVGs in der Sidebar-Selectbox auf reines Weiß setzen (X + Chevron). */
[data-testid="stSidebar"] [data-baseweb="select"] svg,
[data-testid="stSidebar"] [data-baseweb="select"] svg *,
[data-testid="stSidebar"] [data-baseweb="select"] svg path,
[data-testid="stSidebar"] [data-baseweb="select"] svg g,
[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="icon"] svg,
[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="icon"] svg *,
[data-testid="stSidebar"] div[role="combobox"] svg,
[data-testid="stSidebar"] div[role="combobox"] svg *,
[data-testid="stSidebar"] div[role="combobox"] svg path {
  fill: #FFFFFF !important; color: #FFFFFF !important; stroke: #FFFFFF !important;
  opacity: 1 !important; visibility: visible !important;
}
[data-testid="stSidebar"] div[role="combobox"] > div:last-child [role="button"]:hover svg {
  fill: var(--gold-bright) !important; color: var(--gold-bright) !important;
}
/* Expander-Label "Qualifikationslimits anzeigen" — weiß statt grau */
[data-testid="stSidebar"] [data-testid="stExpander"] summary,
[data-testid="stSidebar"] [data-testid="stExpander"] summary *,
[data-testid="stSidebar"] details summary,
[data-testid="stSidebar"] details summary p,
[data-testid="stSidebar"] details summary span {
  color: var(--text) !important; opacity: 1 !important;
}
.profile-meta { display:flex; gap:24px; color:var(--text); font-family:var(--font-mono); font-size:12px;
  letter-spacing:0.08em; text-transform:uppercase; margin:2px 0 18px; flex-wrap:wrap; }
.profile-meta .v { color:var(--text); margin-left:6px; }
.disc-grid { display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:14px; margin-bottom:18px; }
@media (max-width: 900px) { .disc-grid { grid-template-columns:1fr; } }
/* Persönliche Bestleistungen — 3-up Karten oben im Profil */
.pb-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:6px 0 18px; }
@media (max-width:760px) { .pb-grid { grid-template-columns:1fr; } }
.pb-card { background:linear-gradient(180deg,var(--surface),var(--bg-elev));
  border:1px solid var(--gold-dim); border-radius:var(--r-md); padding:14px 18px;
  display:flex; flex-direction:column; gap:4px; min-width:0; }
.pb-card__lab { font-family:var(--font-mono); font-size:11px; letter-spacing:0.14em;
  text-transform:uppercase; color:var(--gold-bright); font-weight:700; }
.pb-card__val { font-family:var(--font-mono); font-size:30px; font-weight:700;
  color:var(--text); line-height:1.05; }
.pb-card__unit { font-size:14px; color:var(--text-2); font-weight:500; margin-left:2px; }
.pb-card__sub { font-family:var(--font-mono); font-size:11.5px; color:var(--text);
  margin-top:2px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
/* disc-tile: gleiche Optik wie pb-card (Gradient + Gold-Dim-Rahmen) */
.disc-tile { background:linear-gradient(180deg,var(--surface),var(--bg-elev));
  border:1px solid var(--gold-dim); border-radius:var(--r-md);
  padding:14px 16px; transition:border-color .14s ease, opacity .14s ease; }
.disc-tile:hover { border-color:var(--gold); }
.disc-tile.empty { opacity:0.55; }
.disc-tile .kicker { font-family:var(--font-mono); font-size:11px; letter-spacing:0.18em;
  text-transform:uppercase; color:var(--gold-bright); font-weight:700; margin-bottom:10px; }
.disc-tile .row { display:flex; justify-content:space-between; align-items:baseline; gap:10px;
  padding:4px 0; border-bottom:1px solid var(--line-soft); }
.disc-tile .row:last-of-type { border-bottom:none; }
.disc-tile .lab { font-family:var(--font-mono); font-size:11px; letter-spacing:0.10em;
  text-transform:uppercase; color:var(--text); }
.disc-tile .val { font-family:var(--font-mono); font-weight:600; font-size:17px;
  color:var(--gold-bright); font-variant-numeric:tabular-nums; }
.disc-tile .foot { margin-top:8px; font-family:var(--font-mono); font-size:10px; letter-spacing:0.08em;
  text-transform:uppercase; color:var(--text-2); }
/* Athleten-Profil-Tabelle: einheitliche Schrift in allen Zellen (IBM Plex Mono),
   damit "Single-ply" nicht visuell aus dem Raster fällt. tabular-nums bleibt für Zahlen. */
.tbl-profile td, .tbl-profile th {
  font-family:var(--font-mono) !important;
}
.tbl-profile td.num, .tbl-profile td.mono, .tbl-profile td.mono-strong,
.tbl-profile td.gold-strong, .tbl-profile th.num {
  font-variant-numeric:tabular-nums;
}

/* === Seiten-Navigation (Segmented-Control = stButtonGroup) — Gold-Theme === */
[data-testid="stButtonGroup"] { gap:6px !important; margin:40px 0 6px;
  border-bottom:1px solid var(--gold-dim); }
[data-testid="stButtonGroup"] button {
  background:transparent !important; border:none !important;
  border-bottom:3px solid transparent !important; border-radius:0 !important;
  box-shadow:none !important;
  font-family:var(--font-mono) !important; font-size:16px !important;
  font-weight:700 !important; letter-spacing:0.14em !important;
  text-transform:uppercase !important;
  color:var(--text-2) !important; padding:12px 22px !important;
  transition:color .12s ease, border-color .12s ease, background .12s ease;
}
[data-testid="stButtonGroup"] button:hover {
  color:var(--gold-bright) !important; background:rgba(201,174,91,0.04) !important;
  border-bottom-color:transparent !important;
}
/* Aktives Segment */
[data-testid="stButtonGroup"] button[kind="segmented_controlActive"] {
  color:var(--gold-bright) !important;
  border-bottom-color:var(--gold-bright) !important;
  background:rgba(201,174,91,0.06) !important;
}
[data-testid="stButtonGroup"] button p,
[data-testid="stButtonGroup"] button div {
  font-weight:700 !important; font-size:16px !important; color:inherit !important;
}

/* === Rekorde-Tabelle === */
.rec-help { display:flex; gap:8px; align-items:center; padding:6px 12px;
  background:var(--bg-elev); border:1px solid var(--gold-dim); border-radius:var(--r-md);
  margin:0 0 6px; font-size:12px; line-height:1.35; color:var(--text-2); }
.rec-help .ico { font-size:14px; color:var(--gold-bright); flex-shrink:0; line-height:1.4; }
.rec-help b { color:var(--text); }
.rec-help .up { color:var(--amber); font-weight:700; }

.rec-filterbar { display:flex; gap:10px; flex-wrap:wrap; margin:6px 0 14px; align-items:center; }

.tbl td.kg-off { color:var(--gold-bright); font-weight:700;
  font-family:var(--font-mono); font-variant-numeric:tabular-nums; }
.tbl td.kg-opl { color:var(--text-2);
  font-family:var(--font-mono); font-variant-numeric:tabular-nums; }
.tbl td.kg-opl.is-higher { color:var(--amber); font-weight:600; }
.tbl td.kg-opl .up { color:var(--amber); margin-left:4px; }
.tbl td.rec-open { color:var(--text-3); font-style:italic; font-weight:400; }
/* Wettkampf-Zelle: Name weiß (gleiche Textgröße wie Haupttabelle), Datum darunter gedämpft */
.tbl td.rec-meet { max-width:260px; }
.tbl td.rec-meet .mname { color:var(--text); font-size:13px; display:block;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.tbl td.rec-meet .mwhen { color:var(--text); font-size:12px;
  font-family:var(--font-mono); font-variant-numeric:tabular-nums; }

/* Rekorde-Tab Selectbox: gleicher Look wie Sidebar, aber Label weiß statt gold */
[data-testid="stTabs"] [data-testid="stSelectbox"] label,
[data-testid="stTabs"] [data-testid="stSelectbox"] label > div,
[data-testid="stTabs"] [data-testid="stSelectbox"] label p,
[data-testid="stTabs"] [data-testid="stWidgetLabel"],
[data-testid="stTabs"] [data-testid="stWidgetLabel"] > div,
[data-testid="stTabs"] [data-testid="stWidgetLabel"] p {
  font-family:var(--font-mono) !important; font-size:14px !important;
  font-weight:600 !important; letter-spacing:0.10em !important;
  text-transform:uppercase !important; color:var(--text) !important;
}
/* Selectboxes: einfacher gold-dim Rahmen NUR am äußeren Wrapper.
   Das innere versteckte combobox-<input> darf KEINEN border haben — wäre sonst
   als 2 px breiter goldener Streifen am linken Rand sichtbar. */
/* Sidebar-Filter (Selectbox + NumberInput): einheitlicher gold-dim Rahmen NUR am
   äußeren Wrapper, innere Elemente transparent. Vom alten Tab-Filter-Styling übernommen. */
[data-testid="stSidebar"] [data-testid="stNumberInput"] > div:not([class*="stWidgetLabel"]):not(label) {
  background:var(--bg-elev) !important;
  border:1px solid var(--gold-dim) !important;
  border-radius:8px !important;
  color:#FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stNumberInput"] > div:not([class*="stWidgetLabel"]):not(label):hover,
[data-testid="stSidebar"] [data-testid="stNumberInput"] > div:not([class*="stWidgetLabel"]):not(label):focus-within {
  border-color:var(--gold) !important;
}
/* Innere Container, base-input, input, Buttons → keine eigenen Borders / Backgrounds. */
[data-testid="stSidebar"] [data-testid="stNumberInput"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-testid="stNumberInput"] [data-baseweb="base-input"],
[data-testid="stSidebar"] [data-testid="stNumberInput"] input,
[data-testid="stSidebar"] [data-testid="stNumberInput"] button {
  background:transparent !important; background-color:transparent !important;
  border:none !important; box-shadow:none !important;
  color:#FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stNumberInput"] button svg,
[data-testid="stSidebar"] [data-testid="stNumberInput"] button path {
  fill:#FFFFFF !important; color:#FFFFFF !important;
}
/* Trennlinie offiziell ↔ OPL */
.tbl td.opl-sep, .tbl th.opl-sep { border-left:1px solid var(--gold-dim); }
/* Rekorde-Tabellen: feste Spaltenausrichtung über alle 4 Disziplinen hinweg */
.tbl-records { table-layout:fixed; min-width:1350px; }
.tbl-records td, .tbl-records th { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

.rec-empty { padding:30px 14px; text-align:center; color:var(--text-3);
  font-family:var(--font-mono); font-size:13px; font-style:italic; }
.rec-disclaimer { font-family:var(--font-mono); font-size:11px; color:var(--text-3);
  line-height:1.5; margin:10px 2px 0; }
.rec-disclaimer b { color:var(--text-2); }

/* Slim top bar shown in profile mode */
.topbar--profile { padding:18px 22px; }
.topbar--profile .brand a { text-decoration:none; color:inherit; display:flex; align-items:center; gap:18px; }
.topbar--profile .pname { font-family:var(--font-display); font-size:26px; font-weight:700; color:var(--text);
  letter-spacing:-0.01em; }
.topbar--profile .psub { font-family:var(--font-mono); font-size:12px; letter-spacing:0.12em;
  text-transform:uppercase; color:var(--gold); margin-top:3px; }
a.back-btn, a.back-btn:link, a.back-btn:visited, a.back-btn:hover, a.back-btn:active {
  color:#111111 !important; text-decoration:none !important;
}
a.back-btn { display:inline-flex; align-items:center; gap:10px; padding:14px 22px;
  background:linear-gradient(180deg, var(--gold-bright) 0%, var(--gold) 100%);
  border:1px solid var(--gold-bright); border-radius:var(--r-md);
  font-family:var(--font-display); font-size:14px; font-weight:700; letter-spacing:0.08em;
  text-transform:uppercase; box-shadow:none;
  transition:transform .14s ease, filter .14s ease; }
a.back-btn:hover { transform:translateY(-1px); filter:brightness(1.05); }
a.back-btn:active { transform:translateY(0); }
a.back-btn .arr { font-size:18px; line-height:1; margin-right:2px; color:#111111 !important; }
/* Qualifikations-Hero im Profil */
.qual-hero { display:flex; align-items:center; justify-content:space-between; gap:18px;
  border-radius:var(--r-lg); padding:18px 22px; margin:6px 0 18px;
  border:1px solid var(--line); background:var(--surface); }
.qual-hero.is-q { border-color:var(--green-line); background:var(--green-bg); }
.qual-hero.is-n { border-color:rgba(217,164,65,0.45); background:rgba(217,164,65,0.10); }
.qual-hero.is-x { border-color:var(--line); }
.qual-hero__l { display:flex; align-items:center; gap:16px; }
.qual-hero__badge { font-family:var(--font-display); font-weight:700; font-size:14px; letter-spacing:0.10em;
  text-transform:uppercase; padding:8px 14px; border-radius:var(--r-sm); white-space:nowrap; }
.qual-hero.is-q .qual-hero__badge { background:var(--green); color:#0B1B0F; }
.qual-hero.is-n .qual-hero__badge { background:var(--amber); color:#1A1206; }
.qual-hero.is-x .qual-hero__badge { background:var(--surface-2); color:var(--text-3); }
.qual-hero__title { font-family:var(--font-display); font-weight:700; font-size:20px; color:var(--text); margin:0; }
.qual-hero__sub { font-family:var(--font-mono); font-size:11px; letter-spacing:0.10em;
  text-transform:uppercase; color:var(--text-3); margin-top:3px; }
.qual-hero__r { font-family:var(--font-mono); font-variant-numeric:tabular-nums;
  font-size:13px; color:var(--text-2); text-align:right; }
.qual-hero__r b { color:var(--gold-bright); font-size:16px; font-weight:700; }
table.tbl tbody td { padding:11px 14px; border-bottom:1px solid var(--line-soft); white-space:nowrap; color:var(--text); text-align:center; }
table.tbl tbody tr:last-child td { border-bottom:none; }
table.tbl tbody tr:hover td { background:var(--surface-3); }
table.tbl tbody tr.tbl-section td { background:rgba(201,174,91,0.10); color:var(--gold-bright);
  font-family:var(--font-mono); font-size:12.5px; letter-spacing:0.10em;
  text-transform:uppercase; padding:8px 12px; font-weight:700;
  border-top:1px solid var(--gold-dim); border-bottom:1px solid var(--gold-dim); }
table.tbl tbody tr.tbl-section:hover td { background:rgba(201,174,91,0.14); }
tr.row--q td { background:transparent; }
tr.row--q:hover td { background:var(--surface-3); }
tr.row--q td:first-child { box-shadow:inset 3px 0 0 var(--green); }
tr.row--w td { background:transparent; }
tr.row--w:hover td { background:var(--surface-3); }
tr.row--w td:first-child { box-shadow:inset 3px 0 0 var(--amber); }
tr.row--n { color:var(--text-2); }
.cell-name .nm { font-weight:600; color:var(--text); font-size:13.5px; }
.cell-name .sub { display:block; font-family:var(--font-mono); font-size:10.5px; color:var(--text-3); margin-top:2px; }
.mono-strong { font-family:var(--font-mono); font-weight:600; font-variant-numeric:tabular-nums; }
.gold-strong { font-family:var(--font-mono); font-weight:600; color:var(--gold); font-variant-numeric:tabular-nums; }
.sex-tag { font-family:var(--font-mono); font-size:14px; font-weight:600; color:var(--text); border:1px solid var(--line); border-radius:4px; padding:3px 9px; }
/* Wettkampftyp-Badge in der Bankdrück-Bestenliste */
.typ-tag { font-family:var(--font-mono); font-size:11px; font-weight:700; letter-spacing:0.06em;
  border-radius:4px; padding:2px 7px; white-space:nowrap; }
.typ-tag.kdk { color:var(--text-2); border:1px solid var(--line); }
.typ-tag.bd  { color:var(--amber); border:1px solid var(--gold-dim); background:rgba(201,174,91,0.10); }
.rank { font-family:var(--font-mono); font-weight:600; color:var(--gold); }

/* Summary cards */
.summaries { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
.sumcard { background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg); overflow:hidden; }
.sumcard__head { padding:14px 20px; border-bottom:1px solid var(--line); }
.sumcard__head h3 { font-family:var(--font-body); font-size:17px; font-weight:700; margin:0; }
.sumrow { display:flex; align-items:center; gap:16px; padding:11px 20px; border-bottom:1px solid var(--line-soft); }
.sumrow:last-child { border-bottom:none; }
.sumrow__label { min-width:120px; font-size:13px; }
.sumrow__label .mono { display:block; font-size:10.5px; color:var(--text-3); }
.sumrow__bar { flex:1; height:8px; border-radius:4px; background:var(--surface-2); overflow:hidden; }
.sumrow__bar i { display:block; height:100%; background:linear-gradient(90deg,var(--gold-dim),var(--gold)); border-radius:4px; }
.sumrow__num { font-family:var(--font-mono); font-weight:600; min-width:28px; text-align:right; color:var(--gold); }
a.sumrow.sumrow--link, a.sumrow.sumrow--link:link, a.sumrow.sumrow--link:visited {
  text-decoration:none !important; color:inherit !important; cursor:pointer;
  transition:background .14s ease;
}
a.sumrow.sumrow--link:hover { background:var(--surface-3); }
a.sumrow.sumrow--link:hover .sumrow__label { color:var(--gold-bright); }

@media (max-width:760px) { .kpis { grid-template-columns:1fr 1fr; } .summaries { grid-template-columns:1fr; }
  .kpi__value { font-size:30px; } }

/* --- Kombinierter Stichtag-Block (Container mit Marker) ---
   Wir markieren den Inhalt mit .__date-card-marker und stylen den umschließenden
   Streamlit-Bordered-Container in Gold. */
.__date-card-marker { display:none; }

[data-testid="stVerticalBlockBorderWrapper"]:has(.__date-card-marker),
[data-testid="stContainer"]:has(.__date-card-marker),
div[data-testid="stVerticalBlock"]:has(> div > [data-testid="element-container"] > [data-testid="stMarkdownContainer"] > .__date-card-marker) {
  background:linear-gradient(180deg,var(--surface),var(--bg-elev)) !important;
  border:1px solid var(--gold-dim) !important;
  border-radius:var(--r-lg) !important;
  padding:18px 22px !important;
  margin-bottom:26px !important;
  box-shadow:0 0 0 1px rgba(201,174,91,0.08) !important;
}

.date-card__title { font-family:var(--font-body); font-size:20px; font-weight:700;
  color:var(--text); margin-top:4px; letter-spacing:-0.005em; line-height:1.25; }

/* Date input — darker, gold-bordered field */
[data-testid="stDateInput"] input, .stDateInput input {
  background:var(--bg-elev) !important; color:var(--text) !important;
  border:1px solid var(--gold-dim) !important; border-radius:var(--r-sm) !important;
  font-family:var(--font-mono) !important; font-size:16px !important;
  padding:10px 14px !important; color-scheme:dark !important;
}
[data-testid="stDateInput"] [data-baseweb="input"] {
  background:var(--bg-elev) !important; border-color:var(--gold-dim) !important;
}

/* --- Klickbare Filter-Zeilen (Vereine / Gewichtsklassen) --- */
div[data-testid="stButton"] > button.filter-row,
.filter-list div[data-testid="stButton"] > button {
  width:100%; text-align:left; justify-content:flex-start;
  background:var(--surface) !important; color:var(--text) !important;
  border:1px solid var(--line-soft) !important; border-radius:var(--r-sm) !important;
  font-family:var(--font-body) !important; font-size:13px !important; font-weight:500 !important;
  padding:10px 14px !important; transition:all .12s ease;
}
.filter-list div[data-testid="stButton"] > button:hover {
  background:var(--surface-3) !important; border-color:var(--gold-dim) !important;
}
.filter-list div[data-testid="stButton"] > button[kind="primary"],
.filter-list div[data-testid="stButton"] > button:focus:not(:active) {
  background:rgba(201,174,91,0.14) !important; border-color:var(--gold) !important;
  color:var(--gold-bright) !important;
}

/* Heading bar for clickable list cards */
.sumcard__head .hint { font-family:var(--font-mono); font-size:10.5px; letter-spacing:0.1em;
  text-transform:uppercase; color:var(--text-3); }
.sumcard__head { display:flex; align-items:center; justify-content:space-between; }

/* ============================================================
   SIDEBAR — überarbeitetes Layout
   ============================================================ */
[data-testid="stSidebar"] > div:first-child { padding-top:14px; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { margin-bottom:0; }

/* Header */
.sb-header {
  display:flex; align-items:center; justify-content:center; gap:10px;
  font-family:var(--font-body); font-size:18px; font-weight:800;
  letter-spacing:0.02em; text-transform:uppercase; color:var(--text);
  padding:4px 0 14px 0; margin-bottom:10px; border-bottom:none;
  position:relative; text-align:center;
}
.sb-header::after {
  content:""; position:absolute; left:0; right:0; bottom:0; height:1px;
  background:linear-gradient(90deg, transparent 0%, var(--gold) 50%, transparent 100%);
  opacity:0.55;
}
.sb-header__bar {
  width:4px; height:18px; background:var(--gold); border-radius:2px;
}

/* Section title */
.sb-section {
  font-family:var(--font-mono); font-size:10.5px; letter-spacing:0.16em;
  text-transform:uppercase; color:var(--gold); font-weight:600;
  margin:18px 0 6px 0; padding-top:14px;
  border-top:1px solid var(--line);
  display:flex; align-items:center; gap:8px;
}
.sb-section--first { margin-top:0; padding-top:0; border-top:none; }
.sb-section::before {
  content:""; width:4px; height:4px; background:var(--gold); border-radius:1px;
}

/* Widget labels in sidebar — refined */
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
  font-family:var(--font-mono) !important; font-size:10.5px !important;
  letter-spacing:0.14em !important; text-transform:uppercase !important;
  color:var(--gold) !important; font-weight:600 !important;
}

/* Multiselect / Selectbox controls — Standard-Rahmen ist gold-dim (siehe Top-Block,
   Zeile ~92). Hier nur die Größe + Fokus-Animation. */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
  min-height:42px; transition:border-color .12s ease;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
  border-color:var(--gold) !important;
  box-shadow:0 0 0 2px rgba(201,174,91,0.18);
}

/* Gewählter Wert im Selectbox (geschlossen) — weiß und größer */
[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="select-value"],
[data-testid="stSidebar"] [data-baseweb="select"] [class*="ValueContainer"],
[data-testid="stSidebar"] [data-baseweb="select"] [class*="SingleValue"],
[data-testid="stSidebar"] [data-baseweb="select"] input,
[data-testid="stSidebar"] [data-baseweb="select"] > div > div:first-child {
  color:#FFFFFF !important; font-family:var(--font-body) !important;
  font-size:14px !important; font-weight:600 !important; letter-spacing:0 !important;
}

/* Dropdown-Menü (Popover) — dunkelgrauer Hintergrund, weißer Text */
[data-baseweb="popover"],
[data-baseweb="popover"] [data-baseweb="menu"],
[data-baseweb="popover"] ul,
[data-baseweb="popover"] [role="listbox"] {
  background:var(--surface-2) !important;
  border:1px solid var(--line) !important;
  border-radius:var(--r-sm) !important;
  box-shadow:var(--shadow-md) !important;
}
[data-baseweb="popover"] [role="option"],
[data-baseweb="popover"] li {
  background:var(--surface-2) !important;
  color:#FFFFFF !important;
  font-family:var(--font-body) !important; font-size:13px !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] li:hover {
  background:var(--surface-3) !important;
  color:#FFFFFF !important;
}
[data-baseweb="popover"] [role="option"][aria-selected="true"],
[data-baseweb="popover"] [aria-selected="true"] {
  color:#FFFFFF !important; background:rgba(201,174,91,0.22) !important; font-weight:600 !important;
}

/* Checkbox "Nur Qualifizierte anzeigen" — Checked-Status grün statt rot.
   Wir überschreiben die roten Default-Streamlit-Farben mit !important und ziel-
   selektoren, die in unterschiedlichen Streamlit-Versionen funktionieren. */
[data-testid="stCheckbox"] label:has(input:checked) > span:first-child,
[data-testid="stCheckbox"] label[data-checked="true"] > span:first-child,
[data-testid="stCheckbox"] label > span[data-checked="true"],
[data-testid="stCheckbox"] span[data-checked="true"],
[data-testid="stCheckbox"] input[type="checkbox"]:checked + span,
[data-testid="stCheckbox"] input[type="checkbox"]:checked ~ span:first-of-type,
[data-testid="stCheckbox"] [aria-checked="true"][role="checkbox"] {
  background-color:#4FB477 !important;
  border-color:#4FB477 !important;
}
/* Auch die roten Background-Styles mit Inline-style überschreiben. */
[data-testid="stCheckbox"] label:has(input:checked) > span:first-child[style],
[data-testid="stCheckbox"] span[data-checked="true"][style] {
  background-color:#4FB477 !important;
  border-color:#4FB477 !important;
}
[data-testid="stCheckbox"] svg { fill:#FFFFFF !important; color:#FFFFFF !important; }

/* Checkbox "Nur Qualifizierte anzeigen" — goldgerahmte Box, mittig, volle Breite */
[data-testid="stSidebar"] [data-testid="stCheckbox"] {
  background:var(--bg-elev) !important; border:1px solid var(--gold-dim) !important;
  border-radius:var(--r-md) !important; padding:12px 14px !important;
  width:100% !important; box-sizing:border-box !important; margin:0 !important;
  display:flex !important; align-items:center !important; justify-content:center !important;
  transition:border-color .12s ease;
}
[data-testid="stSidebar"] [data-testid="stCheckbox"] > label {
  display:flex !important; align-items:center !important; justify-content:center !important;
  gap:10px !important; width:auto !important; margin:0 !important;
}
[data-testid="stSidebar"] [data-testid="stCheckbox"]:hover { border-color:var(--gold-bright) !important; }
[data-testid="stSidebar"] [data-testid="stCheckbox"] label p {
  font-family:var(--font-body) !important; font-size:13px !important;
  letter-spacing:0 !important; text-transform:none !important;
  color:var(--text) !important; font-weight:500 !important;
}
[data-testid="stSidebar"] [data-testid="stCheckbox"] label[data-checked="true"] svg {
  fill:var(--gold) !important;
}

/* ============================================================
   MOBILE (≤ 640 px) — kompakte Meta-Blöcke + Karten-Tabelle
   ============================================================ */
@media (max-width:640px) {
  /* Weniger Innenabstand, engerer Block-Rhythmus */
  [data-testid="stMain"] .block-container,
  .block-container { padding-left:0.8rem !important; padding-right:0.8rem !important; padding-top:0.6rem !important; }
  [data-testid="stMain"] [data-testid="stVerticalBlock"] { gap:16px !important; }

  /* Header kompakter */
  .topbar { flex-direction:column; gap:8px; padding:10px 14px; }
  .brand { margin-right:0 !important; }
  .brand__title { font-size:17px !important; line-height:1.25 !important; }
  .brand__title .beta { font-size:9px !important; padding:1px 5px !important; margin-left:6px !important; }
  .brand__date { font-size:12px !important; }
  .brand__sub { font-size:12px !important; }
  /* Countdown bleibt sichtbar — kompakte einzeilige Variante unter dem Brand */
  .target--solo { padding:8px 14px !important; }
  .target--solo .target__count { flex-direction:row !important;
    align-items:baseline !important; gap:8px !important; }
  .target--solo .target__count .num { font-size:32px !important; }
  .target--solo .target__count .unit { margin-top:0 !important; }

  /* Disclaimer kompakter, linksbündig */
  .dev-banner { font-size:11px !important; padding:8px 10px !important; text-align:left !important;
    line-height:1.35 !important; }

  /* Status-Pills: enges 2×2-Raster statt voller Stapel */
  .data-status { grid-template-columns:1fr 1fr !important; gap:8px !important; }
  .status-pill { flex-direction:column !important; align-items:center !important; gap:2px !important;
    padding:7px 8px !important; }
  .status-pill .lab { font-size:9px !important; }
  .status-pill .val { font-size:11px !important; }

  /* KPI-Karten: eine kompakte Reihe mit 3 Karten */
  .kpis, .kpis--3 { grid-template-columns:repeat(3,1fr) !important; gap:8px !important; }
  .kpi { padding:10px 8px !important; }
  .kpi__label { font-size:9.5px !important; letter-spacing:0.06em !important; margin-bottom:4px !important; }
  .kpi__value { font-size:24px !important; }
  .kpi__foot { font-size:8.5px !important; }

  /* CSV-Export-Button volle Breite */
  [data-testid="stDownloadButton"] > button { width:100% !important; }

  /* --- Tabelle bleibt wie Desktop, scrollt horizontal --- */
  .tablescroll { overflow-x:auto !important; -webkit-overflow-scrolling:touch !important; }
  table.tbl { min-width:100%; }

  /* --- Athletenprofil "Qualifiziert"-Hero: rechte Spalte unter den Status-Block schieben --- */
  .qual-hero { flex-direction:column !important; align-items:stretch !important; gap:10px !important;
    padding:14px 14px !important; }
  .qual-hero__l { width:100% !important; }
  .qual-hero__r { width:100% !important; text-align:left !important; font-size:13px !important;
    padding-top:10px !important; border-top:1px solid rgba(255,255,255,0.10) !important; }
  .qual-hero__r b { font-size:18px !important; }
  .qual-hero__title { font-size:16px !important; line-height:1.3 !important; }
  .qual-hero__sub { font-size:10px !important; line-height:1.4 !important; word-break:break-word !important;
    white-space:normal !important; }
}
</style>
"""


def inject_custom_css():
    st.markdown(THEME_CSS, unsafe_allow_html=True)

# --- KONFIGURATION ---
BASE_PATH = Path(__file__).parent.parent / "meet-data" / "oevk"

QUAL_LIMITS = {
    'F': {'47': 235.0, '52': 265.0, '57': 312.5, '63': 370.0, '69': 380.0, '76': 390.0, '84': 395.0, '84+': 400.0},
    'M': {'59': 420.0, '66': 495.0, '74': 532.5, '83': 625.0, '93': 700.0, '105': 710.0, '120': 715.0, '120+': 720.0},
}
# Flaches Lookup-Dict: (sex, wc_key) -> limit
_QUAL_FLAT: dict = {(sex, wc): lim for sex, wcs in QUAL_LIMITS.items() for wc, lim in wcs.items()}

EVENT_MAP = {'SBD': 'KDK', 'B': 'Bankdrücken', 'BD': 'Bankdrücken'}

GL_COEFFS = {
    # (sex, event_display, equipment) → (a, b, c)
    ('M', 'KDK', 'Raw'):        (1199.72839, 1025.18162, 0.00921),
    ('M', 'KDK', 'Single-ply'): (1236.25115, 1449.21864, 0.01644),
    ('M', 'BD',  'Raw'):        (320.98041,  281.40258,  0.01008),
    ('M', 'BD',  'Single-ply'): (381.22073,  733.79378,  0.02398),
    ('F', 'KDK', 'Raw'):        (610.32796, 1045.59282, 0.03048),
    ('F', 'KDK', 'Single-ply'): (758.63878,  949.31382,  0.02435),
    ('F', 'BD',  'Raw'):        (142.40398,  442.52671,  0.04724),
    ('F', 'BD',  'Single-ply'): (221.82209,  357.00377,  0.02937),
}

# Qualification window for Österreichische Staatsmeisterschaft KDK Classic 2026 (5.–6. September 2026):
# Results count from the day after the 2025 nationals up to but NOT including nationals weekend.
QUAL_WINDOW_START = pd.Timestamp("2025-09-05")
QUAL_WINDOW_END   = pd.Timestamp("2026-09-05")  # championship start — meets ON/after excluded

# Offizielle ÖVK/IPF-Gewichtsklassen (vor PROFILE_MODE definiert, da der Profil-Branch
# st.stop() aufruft und die spätere Sidebar-Definition nie erreicht würde).
FEM_ORDER = ["47", "52", "57", "63", "69", "76", "84", "84+"]
MAL_ORDER = ["59", "66", "74", "83", "93", "105", "120", "120+"]

# --- VEKTORISIERTE DATEN-HELPER ---

def _normalize_wc_key(wc_series: pd.Series) -> pd.Series:
    """Konvertiert WeightClassKg-Strings in QUAL_LIMITS-Schlüssel ('74.00' -> '74', '84+' -> '84+')."""
    wc = wc_series.fillna("").astype(str).str.strip()
    plus_mask = wc.str.contains("+", regex=False)
    result = wc.copy()
    # Plus-Klassen: Dezimalteil entfernen, '+' sicherstellen
    result[plus_mask] = (
        wc[plus_mask]
        .str.split(".").str[0]
        .apply(lambda x: x if x.endswith("+") else x + "+")
    )
    # Normale Klassen: '74.00' -> '74'
    def _to_int_str(x: str) -> str:
        try:
            return str(int(float(x.replace(",", "."))))
        except ValueError:
            return x
    result[~plus_mask] = wc[~plus_mask].apply(_to_int_str)
    return result


def _gl_points_vec(df: pd.DataFrame) -> pd.Series:
    """Vektorisierte IPF-GL-Punkte (4 Disziplinen: KDK/BD × Raw/Single-ply)."""
    result = pd.Series(0.0, index=df.index)
    sex_upper = df["Sex"].astype(str).str.upper().str[:1]
    equip = df["Equipment"].astype(str)
    valid = (df["BodyweightKg"] > 0) & (df["TotalKg"] > 0)

    for (sex, event_display, equipment), (a, b, c) in GL_COEFFS.items():
        event_key = "KDK" if event_display == "KDK" else "Bankdrücken"
        mask = (
            valid
            & (sex_upper == sex)
            & (df["Event_Display"] == event_key)
            & (equip == equipment)
        )
        if not mask.any():
            continue
        bw = df.loc[mask, "BodyweightKg"]
        total = df.loc[mask, "TotalKg"]
        denom = a - b * np.exp(-c * bw)
        result.loc[mask] = (total * 100.0 / denom).round(2)

    return result


def _qual_limits_vec(df: pd.DataFrame) -> pd.Series:
    """Vektorisiertes Qualifikations-Limit-Lookup via Dict-Map."""
    wc_key = _normalize_wc_key(df["WeightClassKg"].astype(str))
    sex = df["Sex"].str.upper()
    return pd.Series(
        [_QUAL_FLAT.get((s, w)) for s, w in zip(sex, wc_key)],
        index=df.index,
        dtype=object,
    )


def _gl_of(sex: str, total: float, bw: float, event: str = "KDK", equip: str = "Raw") -> float:
    """Skalare IPF-GL-Punkte (Standard: KDK Raw) — für die Statistik-Seite.
    Formel wie _gl_points_vec: total*100 / (a - b*exp(-c*bw))."""
    coeffs = GL_COEFFS.get((str(sex).upper()[:1], event, equip))
    if coeffs is None:
        return float("nan")
    a, b, c = coeffs
    try:
        total = float(total); bw = float(bw)
    except (TypeError, ValueError):
        return float("nan")
    if not (bw > 0 and total > 0):
        return float("nan")
    denom = a - b * np.exp(-c * bw)
    if denom <= 0:
        return float("nan")
    return round(total * 100.0 / denom, 2)


def _sh(label: str, sort_type: str = "text", cls: str = "") -> str:
    """Sortierbares Header-Cell — Click wird client-seitig via JS verarbeitet.
    (Modul-Scope, damit alle Seiten inkl. Statistik es nutzen können.)"""
    cls_attr = f' class="{cls} sortable" data-sort-type="{sort_type}"' if cls else ' class="sortable" data-sort-type="{}"'.format(sort_type)
    return f'<th{cls_attr}>{label}<span class="sort-arrow">↕</span></th>'


def _process_entries(df: pd.DataFrame, m_name: str, m_date_raw) -> pd.DataFrame:
    """Aufbereitung der Einträge eines OeVK-Meets (vektorisiert)."""
    # Numerische Spalten
    for col in ("TotalKg", "BodyweightKg"):
        if col in df.columns:
            df[col] = (
                pd.to_numeric(df[col].astype(str).str.replace(",", ".", regex=False), errors="coerce")
                .fillna(0.0).round(2)
            )
        else:
            df[col] = 0.0

    # Beste S/B/D Lifts — fehlende Spalten (ältere Meets) als NaN behandeln
    for col in ("Best3SquatKg", "Best3BenchKg", "Best3DeadliftKg"):
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", ".", regex=False), errors="coerce"
            )
        else:
            df[col] = pd.NA

    # Gewichtsklassen-Anzeigeformat + Sortierkey
    wc = df["WeightClassKg"].astype(str).str.strip()
    plus_mask = wc.str.contains("+", regex=False)
    wc_num = wc.str.replace("+", "", regex=False).str.replace(",", ".", regex=False)
    wc_float = pd.to_numeric(wc_num, errors="coerce").fillna(0.0)
    df["WeightClassKg"] = wc.where(plus_mask, wc_float.map(lambda x: f"{x:.2f}"))
    df["wc_sort"] = wc_float + plus_mask.astype(float) * 0.1

    df["Event_Display"] = df["Event"].str.upper().map(EVENT_MAP).fillna(df["Event"])
    df["GL_Points"] = _gl_points_vec(df)
    df["smLimit"] = _qual_limits_vec(df)

    limit_num = pd.to_numeric(df["smLimit"], errors="coerce")
    df["Differenz"] = (df["TotalKg"] - limit_num).round(2)
    df["Qualifiziert"] = False  # wird in der Sidebar anhand des Datums neu berechnet

    # Alter zum Wettkampftag — bevorzugt BirthDate, sonst BirthYear (Näherung).
    m_date_ts = pd.to_datetime(m_date_raw, errors="coerce")
    age = pd.Series(pd.NA, index=df.index, dtype="object")
    if pd.notna(m_date_ts) and "BirthDate" in df.columns:
        bd = pd.to_datetime(df["BirthDate"], errors="coerce")
        not_birthday_yet = (
            (m_date_ts.month < bd.dt.month)
            | ((m_date_ts.month == bd.dt.month) & (m_date_ts.day < bd.dt.day))
        )
        exact = m_date_ts.year - bd.dt.year - not_birthday_yet.astype("Int64")
        age = exact.where(bd.notna(), other=pd.NA)
    if pd.notna(m_date_ts) and "BirthYear" in df.columns:
        by = pd.to_numeric(df["BirthYear"], errors="coerce")
        approx = m_date_ts.year - by
        # nur fehlende Werte mit dem Näherungs-Alter füllen
        age = pd.Series(age).fillna(approx)
    df["Age"] = age

    # Altersklasse (IPF-Stil) für Rekorde-Tab.
    def _ac(a):
        try:
            if a is None or pd.isna(a):
                return None
            v = float(a)
        except (TypeError, ValueError):
            return None
        if v < 19: return "Jugend"
        if v < 24: return "Junioren"
        if v < 40: return "Open"
        if v < 50: return "AK1"
        if v < 60: return "AK2"
        if v < 70: return "AK3"
        return "AK4"
    df["AgeClass"] = age.map(_ac) if hasattr(age, "map") else pd.Series([_ac(a) for a in age], index=df.index)

    df["MeetName"] = m_name
    df["Date"] = m_date_raw
    return df


# Nur diese Spalten werden geladen — schneller und speichersparender als das volle CSV.
_USE_COLS = ["Name", "Sex", "WeightClassKg", "BodyweightKg", "Team", "TotalKg",
             "Place", "Event", "Equipment", "BirthDate", "BirthYear",
             "Best3SquatKg", "Best3BenchKg", "Best3DeadliftKg"]


# Cache-Buster: hochzählen, wenn sich das Verhalten von aufgerufenen Helfern
# (z. B. _fix_teams / _all_time_team_by_name) ändert, aber der Body von load_data
# selbst gleich bleibt — sonst liefert @st.cache_data alte Ergebnisse.
_LOADER_CACHE_BUST = "teamfix-2"


@st.cache_data(show_spinner="Lade Wettkämpfe …")
def load_data() -> pd.DataFrame:
    """Lädt und verarbeitet alle OeVK-Meets im Qualifikationszeitraum. Ergebnis wird gecacht."""
    _ = _LOADER_CACHE_BUST  # invalidiert den Cache bei Helfer-Änderungen
    if not BASE_PATH.exists():
        return pd.DataFrame()

    all_entries: list = []
    for folder in sorted(BASE_PATH.iterdir()):
        if not folder.is_dir():
            continue
        e_file, m_file = folder / "entries.csv", folder / "meet.csv"
        if not (e_file.exists() and m_file.exists()):
            continue
        try:
            # Datum aus der kleinen meet.csv lesen — out-of-window sofort überspringen.
            with open(m_file, "r", encoding="utf-8", errors="replace") as fh:
                fh.readline()                       # Header
                fields = fh.readline().rstrip("\n").split(",")
            m_date_raw = fields[1] if len(fields) > 1 else ""
            m_name = fields[5] if len(fields) > 5 else folder.name
            m_date_parsed = pd.to_datetime(m_date_raw, errors="coerce")
            if pd.isna(m_date_parsed) or m_date_parsed < QUAL_WINDOW_START:
                continue

            df = pd.read_csv(
                e_file,
                usecols=lambda c: c in _USE_COLS,
                dtype={"WeightClassKg": str, "Team": str, "Equipment": str, "Event": str, "Place": str},
            )
            all_entries.append(_process_entries(df, m_name, m_date_raw))
        except Exception as exc:
            st.warning(f"Fehler beim Laden von {folder.name}: {exc}")

    # EM/WM-Ergebnisse österreichischer Athlet:innen ebenfalls im Qualifikationsfenster berücksichtigen.
    try:
        _intl = load_international_for_austrians()
        if not _intl.empty:
            _dt = pd.to_datetime(_intl.get("Date"), errors="coerce")
            _intl_in_window = _intl[(_dt >= QUAL_WINDOW_START) & (_dt < QUAL_WINDOW_END)]
            if not _intl_in_window.empty:
                all_entries.append(_intl_in_window)
    except Exception:
        pass

    if not all_entries:
        return pd.DataFrame()
    out = pd.concat(all_entries, ignore_index=True)
    return _fix_teams(out)


@st.cache_data(show_spinner=False)
def _all_time_team_by_name() -> dict:
    """Letzter bekannter (nicht-leerer) Verein je Athlet:in aus ALLEN OeVK-Inlandsmeets
    (all-time, nicht nur im Qualifikationsfenster). Länderpokal-Meets werden übersprungen,
    damit keine Fun-Team-Namen als Verein landen. Dient als Fallback, wenn eine Person im
    Fenster keinen Verein eingetragen hat."""
    if not BASE_PATH.exists():
        return {}
    best: dict = {}   # name -> (sortkey_ns, team)
    for folder in sorted(BASE_PATH.iterdir()):
        if not folder.is_dir():
            continue
        e_file, m_file = folder / "entries.csv", folder / "meet.csv"
        if not (e_file.exists() and m_file.exists()):
            continue
        try:
            with open(m_file, "r", encoding="utf-8", errors="replace") as fh:
                fh.readline()
                fields = fh.readline().rstrip("\n").split(",")
            m_date = fields[1] if len(fields) > 1 else ""
            m_name = fields[5] if len(fields) > 5 else ""
            if "länderpokal" in m_name.lower() or "laenderpokal" in m_name.lower():
                continue
            dt = pd.to_datetime(m_date, errors="coerce")
            key = int(dt.value) if pd.notna(dt) else -1
            df = pd.read_csv(e_file, usecols=lambda c: c in ("Name", "Team"))
        except Exception:
            continue
        if "Name" not in df.columns or "Team" not in df.columns:
            continue
        for nm, tm in zip(df["Name"].astype(str), df["Team"].astype(str)):
            t = tm.strip()
            if not t or t.lower() == "nan":
                continue
            prev = best.get(nm)
            if prev is None or key >= prev[0]:
                best[nm] = (key, t)
    return {nm: t for nm, (k, t) in best.items()}


def _fix_teams(out: pd.DataFrame) -> pd.DataFrame:
    """Verein-Daten konsistent machen:
       1) Für EM/WM-Zeilen (_intl=True) **und Länderpokal-Meets** (OeVK-Wettkampf, aber
          mit Fun-Team-Namen wie "Team Vorarlberg" / "OFF1" / "Supakraft Overshoot Gang"):
          Team mit dem zum Wettkampfdatum gültigen Verein aus der **regulären
          Inlandshistorie** überschreiben.
       2) Übrige leere Team-Felder aus dem zuletzt bekannten Team derselben Person füllen.
    """
    if out.empty or "Team" not in out.columns:
        return out
    if "_intl" not in out.columns:
        out["_intl"] = False
    else:
        out["_intl"] = out["_intl"].fillna(False).astype(bool)

    # Länderpokal-Zeilen erkennen (OeVK-Inland, aber Team-Spalte hat Fun-Namen)
    _meetname = out.get("MeetName", pd.Series([""] * len(out))).astype(str)
    _is_laenderpokal = _meetname.str.contains("Länderpokal", case=False, na=False) | \
                        _meetname.str.contains("Laenderpokal", case=False, na=False)
    out["_lp"] = _is_laenderpokal.fillna(False).astype(bool)

    # "Reguläre" Domestik-Einträge: nicht intl UND nicht Länderpokal, mit nicht-leerem Team
    regular = out[(~out["_intl"].astype(bool)) & (~out["_lp"].astype(bool))].copy()
    reg_team = regular["Team"]
    reg_keep = reg_team.notna() & reg_team.astype(str).str.strip().ne("") & reg_team.astype(str).str.lower().ne("nan")
    regular = regular[reg_keep]
    regular["_dt"] = pd.to_datetime(regular.get("Date"), errors="coerce")
    regular = regular[regular["_dt"].notna()]
    pairs_by_name: dict = {}
    for nm, grp in regular.groupby("Name"):
        pairs_by_name[nm] = sorted(zip(grp["_dt"].tolist(), grp["Team"].tolist()))

    def _team_at(name, mdate):
        pairs = pairs_by_name.get(name)
        if not pairs:
            return None
        dt = pd.to_datetime(mdate, errors="coerce")
        if pd.isna(dt):
            return pairs[-1][1]
        prior = [t for d, t in pairs if d <= dt]
        return prior[-1] if prior else pairs[0][1]

    # Schritt 1 — EM/WM- und Länderpokal-Zeilen überschreiben
    override_idx = out.index[out["_intl"].astype(bool) | out["_lp"].astype(bool)]
    for idx in override_idx:
        new_t = _team_at(out.at[idx, "Name"], out.at[idx, "Date"])
        if new_t:
            out.at[idx, "Team"] = new_t

    # Schritt 2 — restliche Empties füllen: bevorzugt aus regulären Domestik-Einträgen,
    # damit Länderpokal-Fun-Names nicht als "Verein" landen.
    if pairs_by_name:
        # neuester regulärer Team-Wert je Person
        latest_by_name = {nm: pairs[-1][1] for nm, pairs in pairs_by_name.items()}
    else:
        latest_by_name = {}
    def _pick(s):
        s2 = s.dropna()
        s2 = s2[s2.astype(str).str.strip().ne("") & s2.astype(str).str.lower().ne("nan")]
        return s2.iloc[0] if not s2.empty else None
    fallback_by_name = out.groupby("Name")["Team"].apply(_pick)
    # Letzter bekannter Verein all-time (auch außerhalb des Fensters) als letzter Fallback,
    # falls im Fenster nie ein Verein eingetragen war.
    all_time = _all_time_team_by_name()
    empty = (
        out["Team"].isna()
        | out["Team"].astype(str).str.strip().eq("")
        | out["Team"].astype(str).str.lower().eq("nan")
    )
    out.loc[empty, "Team"] = out.loc[empty, "Name"].map(
        lambda nm: latest_by_name.get(nm) or fallback_by_name.get(nm) or all_time.get(nm)
    )
    return out


@st.cache_data(show_spinner="Lade Athlet:innen-Historie …")
def load_full_history() -> pd.DataFrame:
    """Lädt ALLE OeVK-Meets ohne Zeitfenster-Filter. Für Athletenprofile."""
    _ = _LOADER_CACHE_BUST  # invalidiert den Cache bei Helfer-Änderungen
    if not BASE_PATH.exists():
        return pd.DataFrame()
    all_entries: list = []
    for folder in sorted(BASE_PATH.iterdir()):
        if not folder.is_dir():
            continue
        e_file, m_file = folder / "entries.csv", folder / "meet.csv"
        if not (e_file.exists() and m_file.exists()):
            continue
        try:
            with open(m_file, "r", encoding="utf-8", errors="replace") as fh:
                fh.readline()
                fields = fh.readline().rstrip("\n").split(",")
            m_date_raw = fields[1] if len(fields) > 1 else ""
            m_name = fields[5] if len(fields) > 5 else folder.name
            df = pd.read_csv(
                e_file,
                usecols=lambda c: c in _USE_COLS,
                dtype={"WeightClassKg": str, "Team": str, "Equipment": str, "Event": str, "Place": str},
            )
            all_entries.append(_process_entries(df, m_name, m_date_raw))
        except Exception:
            # Ältere Meets können fehlende Spalten haben — still überspringen.
            continue

    # EM/WM-Ergebnisse österreichischer Athlet:innen mit aufnehmen (ohne Zeitfenster-Filter).
    try:
        _intl = load_international_for_austrians()
        if not _intl.empty:
            all_entries.append(_intl)
    except Exception:
        pass

    if not all_entries:
        return pd.DataFrame()
    out = pd.concat(all_entries, ignore_index=True)
    return _fix_teams(out)


import unicodedata as _ud

def _norm_name(s) -> str:
    """Case-insensitive, diacritic-stripped match key."""
    try:
        s = str(s)
    except Exception:
        return ""
    return _ud.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower().strip()


@st.cache_data(show_spinner="Lade EM/WM-Ergebnisse …")
def load_international_for_austrians() -> pd.DataFrame:
    """Liefert EM/WM-Ergebnisse österreichischer Athlet:innen.

    Strategie:
      1) Wenn `project-data/oevk_intl.csv` existiert (vorberechnet via
         scripts/build_intl_csv.py — z. B. auf Streamlit Cloud, wo wir
         meet-data/ipf+epf nicht ausliefern), → diese laden + _process_entries
         pro Meet anwenden.
      2) Sonst (lokale Entwicklung mit vollständigem opl-data-Fork) durch
         meet-data/ipf und meet-data/epf laufen und live filtern.

    Identität: (normalisierter Name, Sex, BirthYear).
    """
    # --- Pfad 1: vorberechnete CSV ---
    intl_csv = PROJECT_DATA_DIR / "oevk_intl.csv"
    if intl_csv.exists():
        try:
            raw = pd.read_csv(intl_csv, dtype={"WeightClassKg": str, "Team": str,
                              "Equipment": str, "Event": str, "Place": str,
                              "Name": str, "Sex": str, "BirthYear": str,
                              "_meet_name": str, "_meet_date": str})
        except Exception:
            raw = pd.DataFrame()
        if not raw.empty and "_meet_name" in raw.columns:
            parts: list = []
            for (mname, mdate), grp in raw.groupby(["_meet_name", "_meet_date"], dropna=False):
                df = grp.drop(columns=[c for c in ("_meet_name", "_meet_date") if c in grp.columns]).copy()
                try:
                    _processed = _process_entries(df, str(mname), str(mdate))
                    _processed["_intl"] = True
                    parts.append(_processed)
                except Exception:
                    continue
            if parts:
                return pd.concat(parts, ignore_index=True)
        # CSV vorhanden aber leer/unbrauchbar — kein Live-Fallback erzwingen
        return pd.DataFrame()

    # --- Pfad 2: Live-Scan über meet-data/ipf + meet-data/epf ---
    if not BASE_PATH.exists():
        return pd.DataFrame()

    # Schritt 1: Austrian-Set aus OeVK-Historie aufbauen
    austrians: set = set()
    for folder in BASE_PATH.iterdir():
        if not folder.is_dir():
            continue
        e_file = folder / "entries.csv"
        if not e_file.exists():
            continue
        try:
            d = pd.read_csv(e_file, usecols=lambda c: c in ("Name", "Sex", "BirthYear"),
                            dtype={"Name": str, "Sex": str, "BirthYear": str})
        except Exception:
            continue
        if "Name" not in d.columns:
            continue
        for _, r in d.iterrows():
            nm = _norm_name(r.get("Name", ""))
            sx = str(r.get("Sex", "")).strip().upper()
            by = str(r.get("BirthYear", "")).strip()
            if nm and sx and by and by.lower() != "nan":
                austrians.add((nm, sx, by))

    if not austrians:
        return pd.DataFrame()

    # Schritt 2: IPF + EPF durchsuchen
    intl_root = BASE_PATH.parent  # …/meet-data
    parts: list = []
    for fed in ("ipf", "epf"):
        fed_path = intl_root / fed
        if not fed_path.exists():
            continue
        for folder in fed_path.iterdir():
            if not folder.is_dir():
                continue
            e_file, m_file = folder / "entries.csv", folder / "meet.csv"
            if not (e_file.exists() and m_file.exists()):
                continue
            try:
                with open(m_file, "r", encoding="utf-8", errors="replace") as fh:
                    fh.readline()
                    fields = fh.readline().rstrip("\n").split(",")
                m_date_raw = fields[1] if len(fields) > 1 else ""
                m_name = fields[5] if len(fields) > 5 else f"{fed.upper()} {folder.name}"

                df = pd.read_csv(
                    e_file,
                    usecols=lambda c: c in _USE_COLS,
                    dtype={"WeightClassKg": str, "Team": str, "Equipment": str,
                           "Event": str, "Place": str, "Name": str, "Sex": str, "BirthYear": str},
                )
                # Frühfilter: Equipment Raw, Identität in austrians
                if "Equipment" in df.columns:
                    df = df[df["Equipment"].astype(str) == "Raw"]
                if df.empty:
                    continue
                df["_nm"] = df["Name"].map(_norm_name)
                df["_sx"] = df["Sex"].astype(str).str.upper().str.strip()
                df["_by"] = df["BirthYear"].astype(str).str.strip() if "BirthYear" in df.columns else ""
                mask = [
                    (n, s, b) in austrians
                    for n, s, b in zip(df["_nm"], df["_sx"], df["_by"])
                ]
                df = df[mask].drop(columns=["_nm", "_sx", "_by"])
                if df.empty:
                    continue
                _processed = _process_entries(df, m_name, m_date_raw)
                _processed["_intl"] = True
                parts.append(_processed)
            except Exception:
                continue
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


# --- REKORDE: offizielle ÖVK-Rekordliste + OPL-Dataset-Bestleistungen ---
_RECORDS_COLS = ["sex", "age_class", "equipment", "weight_class", "lift",
                 "record_kg", "athlete", "meet", "date_iso", "notes"]

# PDF-Namen wie "RUTHNER Cornelia" → OPL-Form "Cornelia Ruthner".
# Honorifics/Suffixe (", Mag.", ", II") werden entfernt, damit der Profil-Link auf den OPL-Namen passt.
_HONORIFIC_RE = re.compile(
    r",?\s+(?:Mag\.?|Dr\.?|Ing\.?|Jr\.?|Sr\.?|MSc\.?|BSc\.?|MA\.?|PhD\.?|II|III|IV)$",
    re.IGNORECASE,
)

def normalize_pdf_name(raw: str) -> str:
    if raw is None:
        return ""
    s = str(raw).strip()
    if not s:
        return s
    # Honorifics am Ende entfernen
    while True:
        s2 = _HONORIFIC_RE.sub("", s).strip()
        if s2 == s:
            break
        s = s2
    # Konsekutive führende ALL-CAPS-Tokens als Nachname identifizieren
    tokens = s.split()
    last_idx = 0
    for i, p in enumerate(tokens):
        letters = [c for c in p if c.isalpha()]
        if letters and all(c.isupper() for c in letters):
            last_idx = i + 1
        else:
            break
    if last_idx == 0 or last_idx == len(tokens):
        return s
    last_name = " ".join(tokens[:last_idx]).title()  # titlecased – Bindestriche funktionieren
    first_name = " ".join(tokens[last_idx:])
    return f"{first_name} {last_name}"


@st.cache_data(show_spinner="Lade offizielle Rekorde …")
def load_records() -> pd.DataFrame:
    """Lädt die manuell gepflegte ÖVK-Rekordliste (Quelle der Wahrheit)."""
    p = PROJECT_DATA_DIR / "oevk_records.csv"
    if not p.exists():
        return pd.DataFrame(columns=_RECORDS_COLS)
    try:
        df = pd.read_csv(p, dtype=str).fillna("")
        # record_kg als float
        df["record_kg"] = pd.to_numeric(df["record_kg"].str.replace(",", ".", regex=False),
                                       errors="coerce")
        # Namensformat OPL-konform machen: "RUTHNER Cornelia" → "Cornelia Ruthner"
        if "athlete" in df.columns:
            df["athlete"] = df["athlete"].map(normalize_pdf_name)
        return df
    except Exception:
        return pd.DataFrame(columns=_RECORDS_COLS)


def records_last_updated() -> "datetime | None":
    """Mtime der Rekorde-CSV — für den 'Stand:'-Hinweis."""
    p = PROJECT_DATA_DIR / "oevk_records.csv"
    if not p.exists():
        return None
    try:
        return datetime.fromtimestamp(p.stat().st_mtime)
    except Exception:
        return None


@st.cache_data(show_spinner="Berechne OPL-Bestleistungen …")
def compute_dataset_bests(history: pd.DataFrame) -> pd.DataFrame:
    """Pro (Geschlecht, Altersklasse, Equipment, Gewichtsklasse) die beste Leistung je Disziplin
    aus dem OpenPowerlifting-Datensatz. Long-Form: eine Zeile pro Kombination + Lift.
    Spalten: sex, age_class, equipment, weight_class, lift, kg, athlete, meet, date_iso."""
    if history.empty:
        return pd.DataFrame(columns=["sex", "age_class", "equipment", "weight_class",
                                     "lift", "kg", "athlete", "meet", "date_iso"])
    df = history.copy()
    df = df[df["Equipment"].astype(str).isin(["Raw", "Single-ply"])]
    df = df[df["BodyweightKg"] > 0]
    df["_sex"] = df["Sex"].astype(str).str.upper().str[:1]
    df = df[df["_sex"].isin(["F", "M"])]
    df["_wc"] = df["WeightClassKg"].astype(str).map(wc_display)
    # Total: nur KDK-Wettkämpfe (3-Lift-Meets)
    rows = []
    # Alle Disziplinen NUR aus 3-Lift-Wettkämpfen (KDK) — sonst mischen sich
    # Bankdrücken-only-Meets ein (z. B. Wackernell statt Renner beim KDK-Bankdrücken).
    LIFTS = [
        ("Total",   "TotalKg",         True),
        ("Squat",   "Best3SquatKg",    True),
        ("Bench",   "Best3BenchKg",    True),
        ("Deadlift","Best3DeadliftKg", True),
    ]
    # ÖVK-Cross-Class-Logik (abgeleitet aus dem offiziellen Datenabgleich):
    #   Open      = Maximum über ALLE Altersklassen (Junior, Jugend UND Masters AK1-4
    #               können den Open-Rekord halten, wenn der Lift höher ist)
    #   Junioren  = Maximum über Jugend + Junioren (jüngere "Nachwuchs"-Lifter dürfen
    #               einen Junioren-Rekord setzen)
    #   Jugend, AK1, AK2, AK3, AK4 = jeweils nur innerhalb der eigenen Klasse
    ROLLUP_AGE = {
        "Jugend":   ["Jugend"],
        "Junioren": ["Jugend", "Junioren"],
        "Open":     ["Jugend", "Junioren", "Open", "AK1", "AK2", "AK3", "AK4"],
        "AK1":      ["AK1"],
        "AK2":      ["AK2"],
        "AK3":      ["AK3"],
        "AK4":      ["AK4"],
    }
    grouped_cols = ["_sex", "Equipment", "_wc"]
    for lift_label, col, kdk_only in LIFTS:
        if col not in df.columns:
            continue
        d = df.copy()
        if kdk_only:
            d = d[d["Event_Display"] == "KDK"]
        d["_val"] = pd.to_numeric(d[col], errors="coerce")
        d = d[d["_val"] > 0]
        if d.empty:
            continue
        # Pro Ziel-Altersklasse die Lift-Untermenge der zulässigen Quell-AgeClasses bilden
        # und darüber den Bestwert pro (sex, equip, wc) ermitteln.
        for target_ac, source_acs in ROLLUP_AGE.items():
            d_target = d[d["AgeClass"].isin(source_acs)]
            if d_target.empty:
                continue
            idx = d_target.groupby(grouped_cols, dropna=False)["_val"].idxmax()
            best = d_target.loc[idx, grouped_cols + ["_val", "Name", "MeetName", "Date"]]
            for _, r in best.iterrows():
                rows.append({
                    "sex":          r["_sex"],
                    "age_class":    target_ac,
                    "equipment":    r["Equipment"],
                    "weight_class": r["_wc"],
                    "lift":         lift_label,
                    "kg":           float(r["_val"]),
                    "athlete":      str(r["Name"]),
                    "meet":         str(r["MeetName"]),
                    "date_iso":     str(r["Date"]),
                })
    return pd.DataFrame(rows)


# --- HTML/FORMAT-HELFER (Design-Komponenten) ---
def fmt_kg(value, dec: int = 1) -> str:
    """Deutsche Zahl mit Komma, nachgestellte ',0' entfernt. 532.5 -> '532,5', 430.0 -> '430'."""
    if value is None or pd.isna(value):
        return "–"
    s = f"{float(value):.{dec}f}".replace(".", ",")
    if "," in s:
        s = s.rstrip("0").rstrip(",")
    return s


def fmt_diff(value) -> str:
    """Signierte Differenz mit echtem Minus (U+2212)."""
    if value is None or pd.isna(value):
        return "–"
    v = float(value)
    sign = "+" if v >= 0 else "−"
    return f"{sign}{fmt_kg(abs(v))}"


def diff_class(value) -> str:
    if value is None or pd.isna(value):
        return ""
    v = float(value)
    if v >= 0:
        return "diff--pos"
    if v <= -20:
        return "diff--far"
    return "diff--neg"


def wc_display(wc) -> str:
    """Plain Gewichtsklasse, z. B. '105' oder '120+'. Wird zum Matchen verwendet."""
    s = str(wc).strip()
    if s.endswith("+"):
        return s
    try:
        f = float(s)
        return str(int(f)) if f == int(f) else fmt_kg(f, 2)
    except ValueError:
        return s


def wc_label(wc) -> str:
    """Gewichtsklasse zum Anzeigen — bounded mit führendem Minus ('-105'), '+'-Klassen unverändert."""
    s = wc_display(wc)
    return s if s.endswith("+") or s == "" else f"-{s}"


def sex_display(sex) -> str:
    return {"F": "W", "M": "M"}.get(str(sex).upper(), str(sex))


def fmt_date(value) -> str:
    d = pd.to_datetime(value, errors="coerce")
    return d.strftime("%d.%m.%Y") if pd.notna(d) else ""


def fmt_age(value) -> str:
    try:
        if value is None or pd.isna(value):
            return "–"
        return str(int(float(value)))
    except (ValueError, TypeError):
        return "–"


def fmt_sbd(s, b, d) -> str:
    """Best Squat / Bench / Deadlift als '300 / 200 / 400'. Fehlende/bombed Lifts werden zu '–'."""
    def _one(v):
        try:
            x = float(v)
        except (TypeError, ValueError):
            return "–"
        if pd.isna(x) or x <= 0:
            return "–"
        return fmt_kg(x)
    parts = [_one(s), _one(b), _one(d)]
    return "–" if all(p == "–" for p in parts) else " / ".join(parts)


DISCIPLINES = [
    ("KDK Raw",                "KDK",         "Raw"),
    ("KDK Single-ply",         "KDK",         "Single-ply"),
    ("Bankdrücken Raw",        "Bankdrücken", "Raw"),
    ("Bankdrücken Single-ply", "Bankdrücken", "Single-ply"),
]


def _discipline_best(hist: pd.DataFrame, event_display: str, equip: str) -> dict:
    """Beste Werte (Total, GL, #Wettkämpfe) für eine konkrete Disziplin-Kombination."""
    sub = hist[
        (hist.get("Event_Display").astype(str) == event_display)
        & (hist.get("Equipment").astype(str) == equip)
    ]
    if sub.empty:
        return {"total": float("nan"), "gl": float("nan"), "count": 0}
    totals = pd.to_numeric(sub["TotalKg"], errors="coerce")
    gls = pd.to_numeric(sub.get("GL_Points"), errors="coerce") if "GL_Points" in sub.columns else pd.Series(dtype=float)
    return {
        "total": totals.max() if not totals.empty else float("nan"),
        "gl": gls.max() if not gls.empty else float("nan"),
        "count": int(len(sub)),
    }


def render_athlete_profile(name: str, hist: pd.DataFrame) -> None:
    """Athletenprofil mit Karriereverlauf, Disziplin-Stats, WK-Chart und Wettkampftabelle."""
    h = hist.copy()
    h["_dt"] = pd.to_datetime(h["Date"], errors="coerce")
    # Auf Raw + Single-ply einschränken — alles andere blenden wir aus.
    h["Equipment"] = h["Equipment"].astype(str)
    h = h[h["Equipment"].isin(["Raw", "Single-ply"])]
    h = h.sort_values("_dt", ascending=False)

    if h.empty:
        st.info("Keine Raw- oder Single-ply-Wettkämpfe für " + str(name) + " gefunden.")
        return

    # Meta
    n_meets = h["_dt"].notna().sum()
    first_dt = h["_dt"].min()
    last_dt = h["_dt"].max()
    teams_seen = [t for t in h["Team"].dropna().astype(str).unique() if t.strip()]
    teams_str = ", ".join(teams_seen[:3]) + ("…" if len(teams_seen) > 3 else "")

    # Meta-Strip
    st.markdown(
        '<div class="profile-meta">'
        f'<div>Wettkämpfe<span class="v">{int(n_meets)}</span></div>'
        f'<div>Zeitraum<span class="v">{fmt_date(first_dt) if pd.notna(first_dt) else "–"} → {fmt_date(last_dt) if pd.notna(last_dt) else "–"}</span></div>'
        + (f'<div>Verein<span class="v">{esc(teams_str)}</span></div>' if teams_str else "")
        + '</div>',
        unsafe_allow_html=True,
    )

    # Qualifikations-Status für Staatsmeisterschaft 2026 (Raw + KDK, im Fenster)
    qual_pool = h[
        (h["Equipment"].astype(str) == "Raw")
        & (h.get("Event_Display").astype(str) == "KDK")
        & (h["_dt"] >= QUAL_WINDOW_START)
        & (h["_dt"] < QUAL_WINDOW_END)
    ].copy()
    qual_state = "x"   # x = keine wertbaren Versuche im Fenster
    qual_badge_text = "Nicht ausgewertet"
    qual_title = "Kein wertbarer KDK-Raw-Wettkampf im Qualifikationsfenster"
    qual_sub = f"Fenster: {QUAL_WINDOW_START.strftime('%d.%m.%Y')} – {(QUAL_WINDOW_END - pd.Timedelta(days=1)).strftime('%d.%m.%Y')}"
    qual_right = ""
    if not qual_pool.empty:
        qual_pool["TotalKg"] = pd.to_numeric(qual_pool["TotalKg"], errors="coerce")
        qual_pool = qual_pool.dropna(subset=["TotalKg"])
        if not qual_pool.empty:
            best_idx = qual_pool["TotalKg"].idxmax()
            best_row = qual_pool.loc[best_idx]
            sex_v = str(best_row.get("Sex", "")).upper()[:1]
            wc_disp = wc_display(best_row.get("WeightClassKg"))
            wc_show = wc_label(best_row.get("WeightClassKg"))
            limit = _QUAL_FLAT.get((sex_v, str(wc_disp))) if wc_disp else None
            best_total_v = float(best_row["TotalKg"])
            best_meet = str(best_row.get("MeetName", ""))
            best_date = best_row.get("_dt")
            if limit is not None:
                diff = best_total_v - float(limit)
                if diff >= 0:
                    qual_state = "q"
                    qual_badge_text = "✓ Qualifiziert"
                    qual_title = "Qualifiziert für die Staatsmeisterschaft 2026"
                    qual_sub = f"Limit erreicht in Klasse {wc_show} · {best_meet}" + (
                        f" · {fmt_date(best_date)}" if pd.notna(best_date) else ""
                    )
                    qual_right = (
                        f'<b>{fmt_kg(best_total_v)} kg</b><br>'
                        f'<span style="opacity:.7">Limit {fmt_kg(limit)} kg · +{fmt_kg(diff)} kg</span>'
                    )
                else:
                    qual_state = "n"
                    qual_badge_text = "Noch offen"
                    qual_title = "Noch nicht qualifiziert"
                    qual_sub = f"Beste Leistung in Klasse {wc_show} · {best_meet}" + (
                        f" · {fmt_date(best_date)}" if pd.notna(best_date) else ""
                    )
                    qual_right = (
                        f'<b>{fmt_kg(best_total_v)} kg</b><br>'
                        f'<span style="opacity:.7">Limit {fmt_kg(limit)} kg · −{fmt_kg(abs(diff))} kg</span>'
                    )
    st.markdown(
        f'<div class="qual-hero is-{qual_state}">'
        f'<div class="qual-hero__l">'
        f'<div class="qual-hero__badge">{esc(qual_badge_text)}</div>'
        f'<div><div class="qual-hero__title">{esc(qual_title)}</div>'
        f'<div class="qual-hero__sub">{esc(qual_sub)}</div></div>'
        f'</div>'
        + (f'<div class="qual-hero__r">{qual_right}</div>' if qual_right else "")
        + '</div>',
        unsafe_allow_html=True,
    )

    # --- Persönliche Bestleistungen (beste Einzeldisziplin über alle Raw-Wettkämpfe) ---
    _raw_h = h[h["Equipment"].astype(str) == "Raw"]

    def _best_lift_card(label: str, col: str) -> str:
        if col not in _raw_h.columns or _raw_h.empty:
            return (f'<div class="pb-card"><div class="pb-card__lab">{label}</div>'
                    f'<div class="pb-card__val">–</div></div>')
        s = pd.to_numeric(_raw_h[col], errors="coerce")
        if s.dropna().empty or s.max() <= 0:
            return (f'<div class="pb-card"><div class="pb-card__lab">{label}</div>'
                    f'<div class="pb-card__val">–</div></div>')
        idx = s.idxmax()
        row = _raw_h.loc[idx]
        return (
            f'<div class="pb-card">'
            f'<div class="pb-card__lab">{label}</div>'
            f'<div class="pb-card__val">{fmt_kg(s.loc[idx])}<span class="pb-card__unit"> kg</span></div>'
            f'<div class="pb-card__sub">{esc(str(row.get("MeetName") or ""))}'
            f' · {fmt_date(row.get("Date"))}</div>'
            f'</div>'
        )

    st.markdown(
        '<div class="section-head" style="margin-top:6px"><h2>Persönliche Bestleistungen</h2></div>'
        '<div class="pb-grid">'
        + _best_lift_card("Kniebeugen", "Best3SquatKg")
        + _best_lift_card("Bankdrücken", "Best3BenchKg")
        + _best_lift_card("Kreuzheben", "Best3DeadliftKg")
        + '</div>',
        unsafe_allow_html=True,
    )

    # Disziplin-Kacheln (2x2)
    tiles_html = ['<div class="disc-grid">']
    for label, ev, eq in DISCIPLINES:
        b = _discipline_best(h, ev, eq)
        empty = b["count"] == 0
        tiles_html.append(
            f'<div class="disc-tile{" empty" if empty else ""}">'
            f'<div class="kicker">{esc(label)}</div>'
            f'<div class="row"><span class="lab">Best Total</span><span class="val">{fmt_kg(b["total"]) if not pd.isna(b["total"]) else "–"}</span></div>'
            f'<div class="row"><span class="lab">Best GL</span><span class="val">{fmt_kg(b["gl"], 2) if not pd.isna(b["gl"]) else "–"}</span></div>'
            f'<div class="foot">{b["count"]} Wettk{("ampf" if b["count"] == 1 else "ämpfe")}</div>'
            '</div>'
        )
    tiles_html.append('</div>')
    st.markdown("".join(tiles_html), unsafe_allow_html=True)

    # Total-über-Zeit-Chart — ausschließlich KDK Raw
    chart_df = h.dropna(subset=["_dt"]).copy()
    chart_df["TotalKg"] = pd.to_numeric(chart_df["TotalKg"], errors="coerce")
    chart_df = chart_df.dropna(subset=["TotalKg"])
    chart_df = chart_df[
        (chart_df["Equipment"].astype(str) == "Raw")
        & (chart_df.get("Event_Display").astype(str) == "KDK")
    ]
    if not chart_df.empty:
        fig = go.Figure()
        grp = chart_df.sort_values("_dt")
        color = "#E2C977"
        hovertext = [
            f"{esc(str(mn))}<br>S/B/D: {fmt_sbd(s, b, d)}<br>BW: {fmt_kg(bw, 2)} kg · Klasse: {esc(str(wc))}"
            for mn, s, b, d, bw, wc in zip(
                grp["MeetName"],
                grp.get("Best3SquatKg", pd.Series([None] * len(grp))),
                grp.get("Best3BenchKg", pd.Series([None] * len(grp))),
                grp.get("Best3DeadliftKg", pd.Series([None] * len(grp))),
                grp["BodyweightKg"],
                grp["WeightClassKg"],
            )
        ]
        fig.add_trace(go.Scatter(
            x=grp["_dt"], y=grp["TotalKg"],
            mode="lines+markers", name="KDK Raw",
            line=dict(color=color, width=2),
            marker=dict(size=8, color=color, line=dict(color="#0B0B0C", width=1)),
            hovertext=hovertext,
            hovertemplate="<b>%{x|%d.%m.%Y}</b> · <b>%{y:.1f} kg</b><br>%{hovertext}<extra></extra>",
        ))
        fig.update_layout(
            template="plotly_dark", title=dict(text="Total über Zeit [KDK Raw]", font=dict(color="#E2C977", size=14), x=0, xanchor="left"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=40, b=10), height=320,
            font=dict(family="Archivo, sans-serif", color="#F5F5F4", size=12),
            xaxis=dict(title="", gridcolor="#26262B", zerolinecolor="#26262B"),
            yaxis=dict(title="Total [kg]", gridcolor="#26262B", zerolinecolor="#26262B"),
            showlegend=False,
            hoverlabel=dict(bgcolor="#18181B", bordercolor="#C9AE5B", font_color="#F5F5F4"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Gewichtsklassen-Verlauf (nur wenn ≥2 Meets mit gültiger Klasse)
    wc_df = h.dropna(subset=["_dt"]).copy()
    wc_df["_wc_disp"] = wc_df["WeightClassKg"].astype(str).map(wc_label)
    wc_df = wc_df[wc_df["_wc_disp"].notna() & (wc_df["_wc_disp"] != "")]
    if len(wc_df) >= 2:
        wc_df = wc_df.sort_values("_dt")
        # Achsen-Kategorien NUR aus den tatsächlich besuchten Klassen dieser/dieses
        # Athlet:in — sonst zeigt die plotly-Kategorieachse leere Klassen des anderen
        # Geschlechts (z. B. Herren-Klassen bei einer Frau). Numerisch sortiert, damit
        # auch alte Klassen wie -72 korrekt einsortiert werden ('+'-Klasse nach ihrer Zahl).
        def _wc_sort_key(label: str) -> float:
            base = label.lstrip("-").rstrip("+")
            try:
                v = float(base)
            except ValueError:
                return 9999.0
            return v + (0.5 if label.endswith("+") else 0.0)
        order = sorted(dict.fromkeys(wc_df["_wc_disp"]), key=_wc_sort_key)
        hover_wc = [
            f"{esc(str(mn))}<br>BW: {fmt_kg(bw, 2)} kg · Klasse: {esc(str(wc))}"
            for mn, bw, wc in zip(wc_df["MeetName"], wc_df["BodyweightKg"], wc_df["_wc_disp"])
        ]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=wc_df["_dt"], y=wc_df["_wc_disp"],
            mode="lines+markers",
            line=dict(color="#E2C977", width=2, shape="hv"),
            marker=dict(size=9, color="#E2C977", line=dict(color="#0B0B0C", width=1)),
            hovertext=hover_wc,
            hovertemplate="<b>%{x|%d.%m.%Y}</b> · Klasse <b>%{y}</b><br>%{hovertext}<extra></extra>",
        ))
        fig2.update_layout(
            template="plotly_dark", title=dict(text="Gewichtsklasse über Zeit", font=dict(color="#E2C977", size=14), x=0, xanchor="left"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=40, b=10), height=300,
            font=dict(family="Archivo, sans-serif", color="#F5F5F4", size=12),
            xaxis=dict(title="", gridcolor="#26262B", zerolinecolor="#26262B"),
            yaxis=dict(
                title="", gridcolor="#26262B", zerolinecolor="#26262B",
                type="category", categoryorder="array", categoryarray=order,
            ),
            showlegend=False,
            hoverlabel=dict(bgcolor="#18181B", bordercolor="#C9AE5B", font_color="#F5F5F4"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Vollständige Wettkampftabelle
    head = (
        '<th>Datum</th><th class="l">Wettkampf</th><th>Equip</th><th>Event</th>'
        '<th class="num">Alter</th>'
        '<th>Klasse</th><th class="num">BW</th>'
        '<th class="num">SBD</th>'
        '<th class="num">Total</th>'
        '<th class="num">IPF GL Punkte</th><th class="l">Verein</th>'
    )
    rows = []
    for r in h.itertuples():
        rows.append(
            '<tr>'
            f'<td class="mono">{fmt_date(getattr(r, "_dt", r.Date))}</td>'
            f'<td class="l">{esc(r.MeetName)}</td>'
            f'<td class="mono">{esc(getattr(r, "Equipment", ""))}</td>'
            f'<td class="mono">{esc(getattr(r, "Event_Display", getattr(r, "Event", "")))}</td>'
            f'<td class="num mono">{fmt_age(getattr(r, "Age", None))}</td>'
            f'<td class="mono">{wc_label(r.WeightClassKg)}</td>'
            f'<td class="num mono">{fmt_kg(r.BodyweightKg, 2)}</td>'
            f'<td class="num mono">{fmt_sbd(getattr(r, "Best3SquatKg", None), getattr(r, "Best3BenchKg", None), getattr(r, "Best3DeadliftKg", None))}</td>'
            f'<td class="num mono-strong">{fmt_kg(r.TotalKg)}</td>'
            f'<td class="num gold-strong">{fmt_kg(getattr(r, "GL_Points", None), 2)}</td>'
            f'<td class="l">{esc(getattr(r, "Team", ""))}</td>'
            '</tr>'
        )
    st.markdown(
        '<div class="tablecard" style="margin-top:14px"><div class="tablescroll"><table class="tbl tbl-profile">'
        f'<thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div></div>',
        unsafe_allow_html=True,
    )


def esc(value) -> str:
    return _html.escape("" if value is None or (isinstance(value, float) and pd.isna(value)) else str(value))


def progress_html(total, limit, qualified: bool) -> str:
    """Fortschrittsbalken zum Limit. Limit-Markierung sitzt bei 78% der Breite."""
    if limit is None or pd.isna(limit) or float(limit) <= 0:
        return '<span class="mono" style="color:var(--text-3)">–</span>'
    ratio = float(total) / float(limit)
    fill = max(0.0, min(1.15, ratio)) * 78.0  # 78% = Limit-Position
    cls = "prog__fill--q" if qualified else "prog__fill--n"
    if qualified:
        right = f"Limit {fmt_kg(limit)}"
    else:
        right = f"noch {fmt_kg(float(limit) - float(total))} kg"
    return (
        f'<div class="prog"><div class="prog__track">'
        f'<div class="prog__fill {cls}" style="width:{fill:.1f}%"></div></div>'
        f'<div class="prog__meta"><span>{fmt_kg(total)}</span><span>{esc(right)}</span></div></div>'
    )


def pill_html(qualified: bool) -> str:
    if qualified:
        return '<span class="pill pill--q">✓ Qualifiziert</span>'
    return '<span class="pill pill--n">Offen</span>'


def _filter_qs() -> str:
    """Aktuelle Filter-Selection als URL-Querystring (für Athleten-Links + Back-Button)."""
    parts = []
    t = st.session_state.get("_persist_team")
    if t: parts.append(f"ft={_urlquote(str(t))}")
    n = st.session_state.get("_persist_name")
    if n: parts.append(f"fn={_urlquote(str(n))}")
    s = st.session_state.get("_persist_sex")
    if s and len(s) >= 1: parts.append(f"fs={s[0]}")
    w = st.session_state.get("_persist_wc")
    if w and len(w) == 2:
        parts.append(f"fw={_urlquote(f'{w[0]}:{w[1]}')}")
    m = st.session_state.get("_persist_meet")
    if m: parts.append(f"fm={_urlquote(str(m))}")
    oq = st.session_state.get("_persist_only_qual")
    if oq is False:
        parts.append("foq=0")
    return "&".join(parts)


def kpi_card(label, value, suffix="", icon="", accent=False, foot="", raw_value=False) -> str:
    accent_cls = " kpi--accent" if accent else ""
    suffix_html = f'<span style="font-size:15px;color:var(--text-3);margin-left:4px">{esc(suffix)}</span>' if suffix else ""
    foot_html = f'<div class="kpi__foot">{foot}</div>' if foot else ""
    icon_html = f'<span class="kpi__icon">{icon}</span>' if icon else ""
    value_html = str(value) if raw_value else esc(value)
    return (
        f'<div class="kpi{accent_cls}"><div class="kpi__top">'
        f'<span class="kpi__label">{esc(label)}</span>'
        f'{icon_html}</div>'
        f'<div class="kpi__value">{value_html}{suffix_html}</div>{foot_html}</div>'
    )


# --- UI ---
_favicon_path = PROJECT_DATA_DIR / "oevklogo.png"
st.set_page_config(
    page_title="SM Dashboard 2026",
    layout="wide",
    page_icon=str(_favicon_path) if _favicon_path.exists() else "🏋️",
    initial_sidebar_state="auto",
)
inject_custom_css()

# Sidebar-Fold läuft komplett über Streamlits native Collapse (frontend-only, kein Rerun).
# Die beiden nativen Buttons werden in THEME_CSS als ortsfeste Goldpille gestylt.

# --- Filter-Zustand aus URL-Parametern ?ft=/?fn=/?fs=/?fw=/?fm=/?foq= übernehmen ---
# Wird VOR PROFILE_MODE ausgeführt, damit auch der Back-Button im Profilmodus die
# Filterwerte über _filter_qs() in seine href weitergeben kann.
def _qp_get(key: str):
    v = st.query_params.get(key)
    return v if v not in (None, "") else None

_ft = _qp_get("ft")
if _ft is not None:
    st.session_state["_persist_team"] = _ft
_fn = _qp_get("fn")
if _fn is not None:
    st.session_state["_persist_name"] = _fn
_fs = _qp_get("fs")
if _fs in ("F", "M"):
    st.session_state["_persist_sex"] = ("F", "Frauen") if _fs == "F" else ("M", "Männer")
_fw = _qp_get("fw")
if _fw and ":" in _fw:
    _fw_sex, _fw_wc = _fw.split(":", 1)
    if _fw_sex in ("F", "M"):
        st.session_state["_persist_wc"] = (_fw_sex, _fw_wc)
_fm = _qp_get("fm")
if _fm is not None:
    st.session_state["_persist_meet"] = _fm
_foq = _qp_get("foq")
if _foq is not None:
    st.session_state["_persist_only_qual"] = (_foq != "0")

# Filter-Parameter aus der URL entfernen (wurden in den State übernommen).
for _fk in ("ft", "fn", "fs", "fw", "fm", "foq"):
    try:
        del st.query_params[_fk]
    except (KeyError, AttributeError):
        pass

# --- RESET (Logo / Header-Klick oder Reset-Button) — alle Filter zurücksetzen ---
# Wird ausgeführt VOR den Widget-Definitionen. Wir rotieren zusätzlich einen Widget-Suffix,
# damit Streamlit die Widgets als komplett neue Instanzen behandelt (frontend-side cache).
if st.query_params.get("reset") or st.session_state.get("_reset_requested"):
    for _k in ("team_select", "name_select", "sex_select", "wc_select", "meet_select",
               "date_select", "only_qualified", "athlete",
               "_persist_team", "_persist_name", "_persist_sex", "_persist_wc",
               "_persist_meet", "_persist_only_qual",
               "_reset_requested"):
        if _k in st.session_state:
            del st.session_state[_k]
    # Auch rotations-spezifische alte Keys löschen
    for _k in list(st.session_state.keys()):
        if any(_k.startswith(p) for p in ("team_select_v", "name_select_v", "sex_select_v",
                                          "wc_select_v", "meet_select_v", "only_qualified_v")):
            del st.session_state[_k]
    st.session_state["_widget_gen"] = st.session_state.get("_widget_gen", 0) + 1
    # Beim Reset auch den Sort-State im sessionStorage löschen — das nächste Rendering
    # zeigt dann wieder den Default (IPF GL Punkte ↓).
    st.session_state["_clear_sort_storage"] = True
    st.query_params.clear()
    st.rerun()

# Widget-Generation-Suffixe — PRO SEITE getrennt, damit ein Reset NUR die Widgets seiner
# eigenen Seite zurücksetzt. Beim Reset wird der jeweilige Zähler erhöht → Streamlit behandelt
# die Widgets als neue Instanzen (umgeht den Frontend-Cache, der sonst die alte Anzeige behält).
# Qualifikation: _GEN (_widget_gen) · Rekorde: _GEN_R · Bestenliste: _GEN_T.
_GEN = st.session_state.get("_widget_gen", 0)
_GEN_R = st.session_state.get("_gen_rec", 0)
_GEN_T = st.session_state.get("_gen_topn", 0)
_GEN_S = st.session_state.get("_gen_stat", 0)   # Statistik

def _bump_gen(state_key: str, clear_sort: bool = False):
    """Erhöht einen Seiten-Generation-Zähler (Reset) + rerun."""
    st.session_state[state_key] = st.session_state.get(state_key, 0) + 1
    if clear_sort:
        st.session_state["_clear_sort_storage"] = True
    st.rerun()

# --- PROFILE-MODE (early branch — wenn ?athlete=…, NUR Profil zeigen) ---
_profile_param = st.query_params.get("athlete")
PROFILE_MODE = bool(_profile_param)

# Dashboard-Modus: Sidebar-Fold läuft CLIENT-SEITIG (CSS-Transition + JS-Klick-Handler).
# Keine Server-Roundtrips, keine Reloads — der Sidebar gleitet sanft hinaus/herein.
if not PROFILE_MODE:
    st.markdown(
        '<style>'
        '@media (max-width:900px) {'
        '  .topbar { flex-direction:column; gap:8px; padding:10px 14px; }'
        '  .logo--img img { height:120px !important; }'
        '  .brand { margin-right:0 !important; }'
        '  .brand__title { font-size:20px !important; line-height:1.2 !important; }'
        '  .brand__sub { font-size:13px !important; }'
        '  .target__count .num { font-size:48px !important; }'
        '  .data-status { grid-template-columns:1fr !important; gap:8px !important; }'
        '  .status-pill { flex-direction:column; align-items:center; padding:8px 10px !important;'
        '    text-align:center; gap:2px !important; }'
        '}'
        '</style>',
        unsafe_allow_html=True,
    )

if PROFILE_MODE:
    # Sidebar ausblenden, voller Hauptbereich
    st.markdown(
        '<style>[data-testid="stSidebar"]{display:none!important;} '
        '[data-testid="collapsedControl"]{display:none!important;}</style>',
        unsafe_allow_html=True,
    )
    # Slim Top-Bar: Logo + Back-Button — bewahren die aktuellen Filter via Querystring.
    # Wenn aus Rekorde-Tab kommend (?from=records), den Tab + rec_wc/rec_ac-Filter zurückgeben.
    _back_qs = _filter_qs()
    _from_param = st.query_params.get("from")
    _rec_wc_back = st.query_params.get("rec_wc")
    _rec_ac_back = st.query_params.get("rec_ac")
    _rec_sex_back = st.query_params.get("rec_sex")
    if _from_param == "records":
        _extra = "tab=records"
        if _rec_wc_back:
            _extra += "&rec_wc=" + _urlquote(str(_rec_wc_back))
        if _rec_ac_back:
            _extra += "&rec_ac=" + _urlquote(str(_rec_ac_back))
        if _rec_sex_back:
            _extra += "&rec_sex=" + _urlquote(str(_rec_sex_back))
        _back_qs = (_extra + "&" + _back_qs) if _back_qs else _extra
    elif _from_param == "topn":
        _extra = "tab=topn"
        for _k in ("topn_disc", "topn_sex", "topn_ac", "topn_wc", "topn_n"):
            _v = st.query_params.get(_k)
            if _v:
                _extra += f"&{_k}=" + _urlquote(str(_v))
        _back_qs = (_extra + "&" + _back_qs) if _back_qs else _extra
    _back_href = "?" + _back_qs if _back_qs else "?"
    st.markdown(
        f'''
        <div class="topbar topbar--profile">
          <div class="brand">
            <a href="{_back_href}" target="_self">
              <div>
                <div class="pname">{_html.escape(str(_profile_param))}</div>
                <div class="psub">Athlet:innen-Profil</div>
              </div>
            </a>
          </div>
          <a class="back-btn" href="{_back_href}" target="_self"><span class="arr">←</span> Zurück zum Dashboard</a>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    _hist = load_full_history()
    if _hist.empty:
        st.info("Historische Daten konnten nicht geladen werden.")
    else:
        _rows = _hist[_hist["Name"].astype(str) == str(_profile_param)]
        if _rows.empty:
            st.info("Keine historischen Daten für " + str(_profile_param) + " gefunden.")
        else:
            render_athlete_profile(str(_profile_param), _rows)
    # Credit-Footer
    st.markdown(
        '<div class="credit">Basiert auf Daten von '
        '<a href="https://www.openpowerlifting.org" target="_blank" rel="noopener">openpowerlifting.org</a> · '
        'OpenIPF-Distribution: <a href="https://www.openipf.org" target="_blank" rel="noopener">openipf.org</a></div>',
        unsafe_allow_html=True,
    )
    st.stop()

# --- TOP-HEADER ---
_days = (QUAL_WINDOW_END.normalize() - pd.Timestamp.now().normalize()).days
if _days > 0:
    _count_num, _count_unit = str(_days), "Tage"
elif _days == 0:
    _count_num, _count_unit = "0", "Heute"
else:
    _count_num, _count_unit = "✓", "Absolviert"

st.markdown(
    f"""
    <div class="topbar">
      <a class="brand brand--link" href="?reset=1" target="_self">
        <div>
          <div class="brand__title"><span class="accent">ÖSTERREICHISCHE STAATSMEISTERSCHAFT!</span> Wer ist qualifiziert?<span class="beta">BETA</span></div>
          <div class="brand__date">5. – 6. September 2026</div>
          <div class="brand__sub">Alle Athlet:innen, die das Limit erreicht haben — hier zusammengefasst.</div>
        </div>
      </a>
      <div class="target target--solo">
        <div class="target__count">
          <span class="num">{_count_num}</span>
          <span class="unit">{_count_unit} bis zur SM</span>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

data = load_data()

if data.empty:
    st.warning("Keine Daten gefunden. Bitte sicherstellen, dass meet-data/oevk/ befuellt ist.")
    st.stop()

# --- DATENSTAND / SYNC-STATUS ---
def _fmt_sync_dt(dt):
    if dt is None:
        return "—"
    now = datetime.now()
    today = now.date()
    if dt.date() == today:
        return f"heute, {dt.strftime('%H:%M')}"
    if dt.date() == today - timedelta(days=1):
        return f"gestern, {dt.strftime('%H:%M')}"
    delta_days = (today - dt.date()).days
    if 0 < delta_days <= 7:
        return f"vor {delta_days} Tagen ({dt.strftime('%d.%m.%Y')})"
    return dt.strftime("%d.%m.%Y")

# Marker-Datei "zuletzt geprüft" — Sync-Workflow touched sie bei JEDER Ausführung.
_LAST_CHECK_FILE = Path(__file__).parent.parent / ".last_check"
_last_check_dt = None
try:
    if _LAST_CHECK_FILE.exists():
        _last_check_dt = datetime.fromtimestamp(_LAST_CHECK_FILE.stat().st_mtime)
except Exception:
    pass

# Marker-Datei "Daten zuletzt aktualisiert" — wird NUR getouched, wenn der Workflow
# tatsächlich neue OeVK-Daten von OpenPowerlifting bekommen hat.
_LAST_DATA_FILE = Path(__file__).parent.parent / ".last_data_update"
_last_sync_dt = None
try:
    if _LAST_DATA_FILE.exists():
        _last_sync_dt = datetime.fromtimestamp(_LAST_DATA_FILE.stat().st_mtime)
except Exception:
    pass

_latest_meet_dt = None
_latest_meet_name = None
try:
    _data_dated = data.copy()
    _data_dated["_dt"] = pd.to_datetime(_data_dated["Date"], errors="coerce")
    _data_dated = _data_dated.dropna(subset=["_dt"])
    if not _data_dated.empty:
        _latest_row = _data_dated.loc[_data_dated["_dt"].idxmax()]
        _latest_meet_dt = _latest_row["_dt"]
        _latest_meet_name = str(_latest_row.get("MeetName") or "").strip() or None
except Exception:
    pass

# Stale-Flags (>7 Tage)
def _is_stale(dt):
    return dt is not None and (datetime.now() - dt).days > 7

_check_stale_cls = " is-stale" if (_last_check_dt is None or _is_stale(_last_check_dt)) else ""
_sync_stale_cls  = " is-stale" if _is_stale(_last_sync_dt) else ""

_latest_meet_val = (
    f'{_latest_meet_dt.strftime("%d.%m.%Y")}'
    + (f' · {_html.escape(_latest_meet_name)}' if _latest_meet_name else "")
    if _latest_meet_dt is not None else "—"
)

st.markdown(
    f'<div class="data-status">'
    f'<span class="status-pill{_check_stale_cls}"><span class="dot"></span>'
    f'<span class="lab">Zuletzt nach Updates gesucht</span>'
    f'<span class="val">{_fmt_sync_dt(_last_check_dt) if _last_check_dt is not None else "noch nie"}</span>'
    f'</span>'
    f'<span class="status-pill{_sync_stale_cls}">'
    f'<span class="lab">Daten zuletzt aktualisiert</span>'
    f'<span class="val">{_fmt_sync_dt(_last_sync_dt)}</span>'
    f'</span>'
    f'<span class="status-pill">'
    f'<span class="lab">Letzter Wettkampf</span>'
    f'<span class="val">{_latest_meet_val}</span>'
    f'</span>'
    f'<span class="status-pill">'
    f'<span class="lab">Quellen</span>'
    f'<span class="val">'
    f'<a href="https://www.openpowerlifting.org" target="_blank" rel="noopener">openpowerlifting.org</a>'
    f' · '
    f'<a href="https://www.openipf.org" target="_blank" rel="noopener">openipf.org</a>'
    f'</span>'
    f'</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# Fester Qualifikationszeitraum-Beginn (5. September 2025) — keine UI mehr nötig.
qual_start_date = pd.Timestamp("2025-09-05").date()
meet_dates = pd.to_datetime(data["Date"], errors="coerce")
in_window = meet_dates >= pd.Timestamp(qual_start_date)
limit_num = pd.to_numeric(data["smLimit"], errors="coerce")
data = data.copy()
data["Qualifiziert"] = (data["TotalKg"] >= limit_num) & in_window
data["_wc_disp"] = data["WeightClassKg"].apply(wc_display)

# --- NAVIGATION: Seitenauswahl (ersetzt st.tabs) ---
# Segmented-Control oben im Hauptbereich; die Sidebar zeigt anschließend nur die Filter
# der aktiven Seite. ?tab=records|topn (vom Athleten-Profil-Back-Button) erzwingt die Seite.
_PAGES = ["Qualifikation", "Rekorde", "Bestenliste", "Statistik"]
_url_tab = st.query_params.get("tab")
if _url_tab in ("records", "topn", "stats"):
    st.session_state["_active_page"] = {"records": "Rekorde", "topn": "Bestenliste", "stats": "Statistik"}[_url_tab]
elif "_active_page" not in st.session_state:
    st.session_state["_active_page"] = "Qualifikation"
_page = st.segmented_control("Ansicht", _PAGES, key="_active_page",
                             label_visibility="collapsed")
if _page is None:
    _page = st.session_state.get("_active_page") or "Qualifikation"

# --- SIDEBAR: Filter ---
# Kombinierte Gewichtsklassen-Optionen (Frauen zuerst, dann Männer).
WC_OPTIONS = [("F", w) for w in FEM_ORDER] + [("M", w) for w in MAL_ORDER]


def _fmt_wc_option(opt) -> str:
    sex, wc = opt
    sex_label = "Frauen" if sex == "F" else "Männer"
    return f"{sex_label} · {wc_label(wc)} kg"


_PERSIST_PAIRS = (
    (f"team_select_v{_GEN}",     "_persist_team"),
    (f"name_select_v{_GEN}",     "_persist_name"),
    (f"sex_select_v{_GEN}",      "_persist_sex"),
    (f"wc_select_v{_GEN}",       "_persist_wc"),
    (f"meet_select_v{_GEN}",     "_persist_meet"),
    (f"only_qualified_v{_GEN}",  "_persist_only_qual"),
)
for _wkey, _pkey in _PERSIST_PAIRS:
    if _wkey not in st.session_state and _pkey in st.session_state:
        st.session_state[_wkey] = st.session_state[_pkey]


team_options = sorted(data["Team"].dropna().unique())

# URL-Query-Parameter ?team=… (z. B. von Klick auf Verein-Balken) hat Vorrang über den Persist-Wert.
_url_team = st.query_params.get("team")
if _url_team and _url_team in team_options:
    st.session_state["_persist_team"] = _url_team
    st.session_state[f"team_select_v{_GEN}"] = _url_team
    try:
        del st.query_params["team"]
    except (KeyError, AttributeError):
        pass


def _idx_of(options, value):
    """Index der Persist-Selection in den aktuellen Optionen — sonst None."""
    if value is None:
        return None
    try:
        return options.index(value)
    except (ValueError, TypeError):
        return None


if _page == "Qualifikation":
    selected_team = st.sidebar.selectbox(
        "Verein",
        team_options,
        index=None,
        placeholder="Verein wählen",
        key=f"team_select_v{_GEN}",
    )

    # Wenn kein Verein gewählt ist, alle Athlet:innen anzeigen.
    if selected_team:
        available_names = sorted(data.loc[data["Team"] == selected_team, "Name"].dropna().unique())
    else:
        available_names = sorted(data["Name"].dropna().unique())
    selected_name = st.sidebar.selectbox(
        "Athlet:in",
        available_names,
        index=None,
        placeholder="Athlet:in wählen",
        key=f"name_select_v{_GEN}",
    )

    # Geschlechts-Filter
    _SEX_OPTIONS = [("F", "Frauen"), ("M", "Männer")]
    selected_sex = st.sidebar.selectbox(
        "Geschlecht",
        _SEX_OPTIONS,
        index=None,
        format_func=lambda opt: opt[1],
        placeholder="Geschlecht wählen",
        key=f"sex_select_v{_GEN}",
    )

    selected_wc = st.sidebar.selectbox(
        "Gewichtsklasse",
        WC_OPTIONS,
        index=None,
        format_func=_fmt_wc_option,
        placeholder="Gewichtsklasse wählen",
        key=f"wc_select_v{_GEN}",
    )

    # Wettkampf-Filter — Optionen orientieren sich am bereits aktiven Zeitraum (Raw + KDK).
    _meet_pool = data[in_window & (data["Equipment"] == "Raw") & (data["Event_Display"] == "KDK")]
    meet_options = sorted(_meet_pool["MeetName"].dropna().unique())
    selected_meet = st.sidebar.selectbox(
        "Wettkampf",
        meet_options,
        index=None,
        placeholder="Wettkampf wählen",
        key=f"meet_select_v{_GEN}",
    )

    # Filter-Reset-Button (nur Qualifikations-Filter) — Generation-Bump + Sort-Reset.
    if st.sidebar.button("↺ Filter zurücksetzen", key="reset_filters_btn"):
        for _pk in ("_persist_team", "_persist_name", "_persist_sex", "_persist_wc",
                    "_persist_meet", "_persist_only_qual"):
            st.session_state.pop(_pk, None)
        _bump_gen("_widget_gen", clear_sort=True)

    # Checkbox am Ende — getrennt durch Goldlinie.
    # Default vor dem Widget setzen (statt value=…), damit Streamlit nicht warnt, wenn
    # der Key bereits aus _persist_only_qual oder einem früheren Run im Session-State steht.
    st.sidebar.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
    if f"only_qualified_v{_GEN}" not in st.session_state:
        _persist_only_qual = st.session_state.get("_persist_only_qual")
        st.session_state[f"only_qualified_v{_GEN}"] = (
            True if _persist_only_qual is None else bool(_persist_only_qual)
        )
    show_only_qualified = st.sidebar.checkbox(
        "Nur Qualifizierte anzeigen",
        key=f"only_qualified_v{_GEN}",
    )

    # Aktuelle Widget-Werte in die _persist_*-Keys spiegeln, damit sie nach PROFILE_MODE bestehen.
    for _wkey, _pkey in _PERSIST_PAIRS:
        if _wkey in st.session_state:
            st.session_state[_pkey] = st.session_state[_wkey]

    # --- SM-Limits (offizielle Qualifikationsgrenzen je Klasse) ---
    _lim_rows_f = "".join(
        f'<tr><td class="lim-wc">{("-" + wc) if not wc.endswith("+") else wc}</td>'
        f'<td class="lim-val">{fmt_kg(QUAL_LIMITS["F"][wc])}</td></tr>'
        for wc in FEM_ORDER
    )
    _lim_rows_m = "".join(
        f'<tr><td class="lim-wc">{("-" + wc) if not wc.endswith("+") else wc}</td>'
        f'<td class="lim-val">{fmt_kg(QUAL_LIMITS["M"][wc])}</td></tr>'
        for wc in MAL_ORDER
    )
    st.sidebar.markdown(
        '<div class="sb-divider"></div>'
        '<div class="lim-card">'
        '<div class="lim-head">Qualifikationslimits</div>'
        '<div class="lim-cap">Frauen</div>'
        f'<table class="lim-tbl">{_lim_rows_f}</table>'
        '<div class="lim-cap">Männer</div>'
        f'<table class="lim-tbl">{_lim_rows_m}</table>'
        '<div class="lim-foot">Werte in kg · KDK Raw</div>'
        '</div>',
        unsafe_allow_html=True,
    )

else:
    # Auf anderen Seiten existieren die Qualifikations-Filter nicht — Defaults setzen,
    # damit die (global laufende) Pipeline keine NameErrors wirft.
    selected_team = selected_name = selected_sex = selected_wc = selected_meet = None
    show_only_qualified = True
# --- DATEN-BASIS: nur Raw + KDK gelten als Qualifikation, alles andere ignorieren ---
df_scope = data[(data["Equipment"] == "Raw") & (data["Event_Display"] == "KDK") & in_window]

# Baseline für Summary-Boxen — folgt Verein-, Klassen- und Wettkampf-Filter.
df_baseline_scope = df_scope
if selected_team:
    df_baseline_scope = df_baseline_scope[df_baseline_scope["Team"] == selected_team]
if selected_sex:
    df_baseline_scope = df_baseline_scope[
        df_baseline_scope["Sex"].astype(str).str.upper().str[:1] == selected_sex[0]
    ]
if selected_wc:
    sex_b, wc_b = selected_wc
    sex_u_b = df_baseline_scope["Sex"].astype(str).str.upper()
    df_baseline_scope = df_baseline_scope[(sex_u_b == sex_b) & (df_baseline_scope["_wc_disp"] == wc_b)]
if selected_meet:
    df_baseline_scope = df_baseline_scope[df_baseline_scope["MeetName"] == selected_meet]
qual_baseline = df_baseline_scope[df_baseline_scope["Qualifiziert"]]
best_baseline = (
    qual_baseline.sort_values("TotalKg", ascending=False).drop_duplicates("Name")
)

# --- FILTER (Verein + Klasse + Wettkampf + Athlet:in auf die Haupt-Tabelle anwenden) ---
df_filtered = df_scope
if selected_team:
    df_filtered = df_filtered[df_filtered["Team"] == selected_team]
if selected_sex:
    df_filtered = df_filtered[
        df_filtered["Sex"].astype(str).str.upper().str[:1] == selected_sex[0]
    ]
if selected_wc:
    sex_f, wc_f = selected_wc
    sex_u = df_filtered["Sex"].astype(str).str.upper()
    df_filtered = df_filtered[(sex_u == sex_f) & (df_filtered["_wc_disp"] == wc_f)]
if selected_meet:
    df_filtered = df_filtered[df_filtered["MeetName"] == selected_meet]
if selected_name:
    df_filtered = df_filtered[df_filtered["Name"] == selected_name]

df_filtered = df_filtered.sort_values(["Sex", "wc_sort"])

# --- KPI-KARTEN ---
n_athletes = df_filtered["Name"].nunique()
n_meets = df_filtered["MeetName"].nunique()

# Qualifizierte: gesamt + Aufteilung nach Geschlecht (eindeutige Personen)
_qual_unique = (
    df_filtered[df_filtered["Qualifiziert"] == True]
    .drop_duplicates("Name")
)
n_qual = len(_qual_unique)
n_qual_f = int((_qual_unique["Sex"].astype(str).str.upper() == "F").sum())
n_qual_m = int((_qual_unique["Sex"].astype(str).str.upper() == "M").sum())

# Gesamt-Teilnehmer:innen je Geschlecht (Basis: alle gefilterten Athlet:innen)
_all_unique = df_filtered.drop_duplicates("Name")
n_f = int((_all_unique["Sex"].astype(str).str.upper() == "F").sum())
n_m = int((_all_unique["Sex"].astype(str).str.upper() == "M").sum())

# Quote der Qualifizierten an allen Teilnehmer:innen je Geschlecht
def _pct(part, total):
    return round(part / total * 100, 1) if total else 0
_qf_rate = _pct(n_qual_f, n_f)
_qm_rate = _pct(n_qual_m, n_m)
qual_foot = (
    f'<span style="color:var(--gold);font-weight:600">Frauen · {n_qual_f} / {n_f} ({_qf_rate}%)</span>'
    f'<span style="opacity:0.4;margin:0 8px">|</span>'
    f'<span style="color:var(--gold);font-weight:600">Männer · {n_qual_m} / {n_m} ({_qm_rate}%)</span>'
)

# Wettkämpfe-Aufschlüsselung: national (OeVK) vs. EM/WM (intl)
if "_intl" in df_filtered.columns:
    _meet_intl_map = df_filtered.groupby("MeetName")["_intl"].any()
    n_meets_intl = int(_meet_intl_map.sum())
    n_meets_nat  = int((~_meet_intl_map).sum())
else:
    n_meets_intl = 0
    n_meets_nat = n_meets
meets_foot = (
    f'<span style="color:var(--gold);font-weight:600">National · {n_meets_nat}</span>'
    f'<span style="opacity:0.4;margin:0 8px">|</span>'
    f'<span style="color:var(--gold);font-weight:600">EM/WM · {n_meets_intl}</span>'
)

# Geschlechterverteilung (alle Athlet:innen im Filterscope) — als Fuß in der Athlet:innen-Karte
_ath_total = max(n_f + n_m, 1)
_ath_pct_f = round(n_f / _ath_total * 100)
_ath_pct_m = 100 - _ath_pct_f if (n_f + n_m) > 0 else 0
athlete_foot = (
    f'<span style="color:var(--gold);font-weight:600">Frauen · {n_f} ({_ath_pct_f}%)</span>'
    f'<span style="opacity:0.4;margin:0 8px">|</span>'
    f'<span style="color:var(--gold);font-weight:600">Männer · {n_m} ({_ath_pct_m}%)</span>'
)

# --- Rekorde-Tab Rückkehr-Zustand aus URL ---
# Wenn der Benutzer vom Athleten-Profil aus dem Rekorde-Tab zurückkommt (?tab=records&rec_wc=F-47),
# (a) Filter wiederherstellen, (b) JS-Snippet klickt nach dem Rendern den zweiten Tab.
_url_tab = st.query_params.get("tab")
_url_rec_wc = st.query_params.get("rec_wc")
_url_rec_ac = st.query_params.get("rec_ac")
_url_rec_sex = st.query_params.get("rec_sex")
if _url_rec_wc and f"rec_wc_v{_GEN_R}" not in st.session_state:
    try:
        _rsex, _rwc = str(_url_rec_wc).split("-", 1)
        if (_rsex, _rwc) in WC_OPTIONS:
            st.session_state[f"rec_wc_v{_GEN_R}"] = (_rsex, _rwc)
    except Exception:
        pass
if _url_rec_ac and f"rec_age_v{_GEN_R}" not in st.session_state:
    if _url_rec_ac in ("Jugend", "Junioren", "Open", "AK1", "AK2", "AK3", "AK4"):
        st.session_state[f"rec_age_v{_GEN_R}"] = _url_rec_ac
if _url_rec_sex and f"rec_sex_v{_GEN_R}" not in st.session_state:
    if _url_rec_sex in ("F", "M"):
        st.session_state[f"rec_sex_v{_GEN_R}"] = (_url_rec_sex, "Frauen" if _url_rec_sex == "F" else "Männer")

# Bestenliste-Tab Rückkehr-Zustand aus URL
_DISC_OPTS = ["KDK (Total)", "Bankdrücken (alle)", "Bankdrücken (nur BD-Wettkämpfe)"]
_url_topn_disc = st.query_params.get("topn_disc")
_url_topn_sex = st.query_params.get("topn_sex")
_url_topn_ac = st.query_params.get("topn_ac")
_url_topn_wc = st.query_params.get("topn_wc")
_url_topn_n = st.query_params.get("topn_n")
if _url_topn_disc and f"topn_disc_v{_GEN_T}" not in st.session_state:
    if _url_topn_disc in _DISC_OPTS:
        st.session_state[f"topn_disc_v{_GEN_T}"] = _url_topn_disc
if _url_topn_sex and f"topn_sex_v{_GEN_T}" not in st.session_state:
    if _url_topn_sex in ("F", "M"):
        st.session_state[f"topn_sex_v{_GEN_T}"] = (_url_topn_sex, "Frauen" if _url_topn_sex == "F" else "Männer")
if _url_topn_ac and f"topn_age_v{_GEN_T}" not in st.session_state:
    if _url_topn_ac in ("Jugend", "Junioren", "Open", "AK1", "AK2", "AK3", "AK4"):
        st.session_state[f"topn_age_v{_GEN_T}"] = _url_topn_ac
if _url_topn_wc and f"topn_wc_v{_GEN_T}" not in st.session_state:
    try:
        _tsex, _twc = str(_url_topn_wc).split("-", 1)
        if (_tsex, _twc) in WC_OPTIONS:
            st.session_state[f"topn_wc_v{_GEN_T}"] = (_tsex, _twc)
    except Exception:
        pass
if _url_topn_n and f"topn_n_v{_GEN_T}" not in st.session_state:
    try:
        _n_val = int(_url_topn_n)
        if 1 <= _n_val <= 5000:
            st.session_state[f"topn_n_v{_GEN_T}"] = _n_val
    except Exception:
        pass

# Filter-/Seiten-Zustand wurde aus der URL in session_state übernommen — URL aufräumen,
# damit ein späterer Sidebar-Rerun nicht erneut auf alte Werte springt.
if _url_tab in ("records", "topn"):
    try:
        for _p in ("tab", "from",
                   "rec_wc", "rec_ac", "rec_sex",
                   "topn_disc", "topn_sex", "topn_ac", "topn_wc", "topn_n"):
            if _p in st.query_params:
                del st.query_params[_p]
    except Exception:
        pass

if _page == "Qualifikation":
    st.markdown(
        '<div class="kpis kpis--3">'
        + kpi_card("Qualifiziert", n_qual, accent=True, foot=qual_foot)
        + kpi_card("Athlet:innen", n_athletes, foot=athlete_foot)
        + kpi_card("Wettkämpfe", n_meets, foot=meets_foot)
        + "</div>",
        unsafe_allow_html=True,
    )

    # --- ATHLET:INNEN-TABELLE (Bestleistung je Person) ---
    qual_df = df_filtered[df_filtered["Qualifiziert"] == True]

    if show_only_qualified:
        table_df = qual_df
        section_title = "Qualifizierte Athlet:innen"
    else:
        table_df = df_filtered
        section_title = "Athlet:innen"

    # Bestleistung pro Person (höchstes Total). Default-Sortierung: Qualifizierte zuerst,
    # dann IPF GL Punkte absteigend. (Wird auch für den CSV-Export verwendet.)
    if not table_df.empty:
        best_per_athlete = (
            table_df.sort_values("TotalKg", ascending=False).drop_duplicates("Name")
        )
        best_per_athlete = best_per_athlete.sort_values(
            by=["Qualifiziert", "GL_Points"],
            ascending=[False, False],
            na_position="last",
        )
    else:
        best_per_athlete = table_df

    # Export-Frame (exakt die angezeigte Tabelle) → CSV (Deutsch-Excel-freundlich).
    def _build_export_df(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for i, r in enumerate(df.itertuples(), start=1):
            rows.append({
                "#": i,
                "Name": r.Name,
                "Geschlecht": sex_display(r.Sex),
                "Alter": fmt_age(r.Age),
                "Körpergewicht (kg)": fmt_kg(r.BodyweightKg, 2),
                "Gewichtsklasse (kg)": wc_label(r.WeightClassKg),
                "Total (kg)": fmt_kg(r.TotalKg),
                "SBD (kg)": fmt_sbd(getattr(r, "Best3SquatKg", None), getattr(r, "Best3BenchKg", None), getattr(r, "Best3DeadliftKg", None)),
                "SM Limit (kg)": fmt_kg(r.smLimit),
                "Differenz (kg)": fmt_diff(r.Differenz),
                "IPF GL Punkte": fmt_kg(r.GL_Points, 2),
                "Verein": r.Team,
                "Wettkampf": r.MeetName,
                "Wettkampfdatum": fmt_date(r.Date),
            })
        return pd.DataFrame(rows)

    # CSV-Export-Button rechts neben der Section-Headline (vertikal mittig).
    _hdr_left, _hdr_right = st.columns([4, 1], vertical_alignment="center")
    with _hdr_left:
        st.markdown(
            f'<div class="section-head"><div>'
            f'<h2>{section_title}</h2></div></div>',
            unsafe_allow_html=True,
        )
    with _hdr_right:
        if not table_df.empty:
            _export_df = _build_export_df(best_per_athlete)
            _csv_bytes = _export_df.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                "⬇ CSV-Export",
                data=_csv_bytes,
                file_name="oevk_qualifikation.csv",
                mime="text/csv",
                key="dl_csv",
                use_container_width=True,
            )

    if not table_df.empty:
        _q_head = (
            '<th class="num nosort">#</th>'
            + _sh("Name", "text")
            + _sh("Geschlecht", "text")
            + _sh("Alter", "num", "num")
            + _sh("Körpergewicht", "num", "num")
            + '<th class="nosort">Gewichtsklasse</th>'
            + _sh("Total", "num", "num")
            + '<th class="num nosort">SBD</th>'
            + _sh("SM Limit", "num", "num")
            + _sh("Differenz", "diff")
            + _sh("IPF GL Punkte", "num", "num")
            + _sh("Verein", "text")
            + _sh("Wettkampf", "text")
            + _sh("Wettkampfdatum", "date")
        )
        _q_rows = []
        for i, r in enumerate(best_per_athlete.itertuples(), start=1):
            q = bool(r.Qualifiziert)
            row_cls = "row--q" if q else "row--w"
            _fqs = _filter_qs()
            _athlete_href = f"?athlete={_urlquote(str(r.Name))}" + (f"&{_fqs}" if _fqs else "")
            _name_link = f'<a class="nm nm-link" href="{_athlete_href}" target="_self">{esc(r.Name)}</a>'
            _q_rows.append(
                f'<tr class="{row_cls}">'
                f'<td class="num rank" data-label="">{i}</td>'
                f'<td class="cell-name l" data-label="Name">{_name_link}</td>'
                f'<td data-label="Geschlecht"><span class="sex-tag">{sex_display(r.Sex)}</span></td>'
                f'<td class="num mono" data-label="Alter">{fmt_age(r.Age)}</td>'
                f'<td class="num mono" data-label="Körpergewicht">{fmt_kg(r.BodyweightKg, 2)}</td>'
                f'<td class="mono" data-label="Gewichtsklasse">{wc_label(r.WeightClassKg)}</td>'
                f'<td class="num mono-strong" data-label="Total">{fmt_kg(r.TotalKg)}</td>'
                f'<td class="num mono" data-label="SBD">{fmt_sbd(getattr(r, "Best3SquatKg", None), getattr(r, "Best3BenchKg", None), getattr(r, "Best3DeadliftKg", None))}</td>'
                f'<td class="num mono" data-label="SM Limit">{fmt_kg(r.smLimit)}</td>'
                f'<td data-label="Differenz"><span class="diff {diff_class(r.Differenz)}">{fmt_diff(r.Differenz)}</span></td>'
                f'<td class="num gold-strong" data-label="IPF GL Punkte">{fmt_kg(r.GL_Points, 2)}</td>'
                f'<td class="l" data-label="Verein">{esc(r.Team)}</td>'
                f'<td class="l" data-label="Wettkampf">{esc(r.MeetName)}</td>'
                f'<td class="mono" data-label="Wettkampfdatum">{fmt_date(r.Date)}</td></tr>'
            )
        st.markdown(
            f'<div class="tablecard" id="qual-tablecard"><div class="tablescroll"><table class="tbl" id="qual-table">'
            f'<thead><tr>{_q_head}</tr></thead><tbody>{"".join(_q_rows)}</tbody></table></div></div>',
            unsafe_allow_html=True,
        )
        # Wenn ein Reset stattgefunden hat, vorab den persistierten Sort-State löschen.
        if st.session_state.pop("_clear_sort_storage", False):
            _components.html(
                """
    <script>
    (function(){ try { window.parent.sessionStorage.removeItem('oevk_sort_state_v1'); } catch(e){} })();
    </script>
                """,
                height=0,
            )

        # Client-seitiger Sort — kein Streamlit-Rerun, kein Flash.
        _components.html(
            """
    <script>
    (function () {
      const doc = window.parent.document;
      const SS = window.parent.sessionStorage;
      const SORT_KEY = 'oevk_sort_state_v1';
      function loadState() {
        try { const raw = SS.getItem(SORT_KEY); if (!raw) return null; const o = JSON.parse(raw);
              if (typeof o.col === 'number' && (o.dir === 'asc' || o.dir === 'desc')) return o; }
        catch (e) {}
        return null;
      }
      function saveState(s) { try { SS.setItem(SORT_KEY, JSON.stringify(s)); } catch (e) {} }

      function parseNum(s) {
        if (!s) return NaN;
        // Echtes Minus (U+2212, aus fmt_diff) zuerst auf ASCII-Minus normalisieren —
        // sonst strippt die Zeichenklasse unten das Vorzeichen und negative
        // Differenzen werden als positive Beträge sortiert.
        s = s.replace(/\\u2212/g, '-').replace(/\\s/g, '').replace(/[^\\-+\\d.,]/g, '').replace(',', '.');
        const f = parseFloat(s);
        return isNaN(f) ? NaN : f;
      }
      function parseDate(s) {
        const m = (s || '').trim().match(/^(\\d{1,2})[.\\/](\\d{1,2})[.\\/](\\d{2,4})$/);
        if (!m) return NaN;
        const d = parseInt(m[1], 10), mo = parseInt(m[2], 10) - 1;
        let y = parseInt(m[3], 10); if (y < 100) y += 2000;
        return new Date(y, mo, d).getTime();
      }
      function valueOf(row, idx, type) {
        const cell = row.children[idx];
        if (!cell) return null;
        const text = (cell.textContent || '').trim();
        if (type === 'num' || type === 'diff') { const v = parseNum(text); return isNaN(v) ? null : v; }
        if (type === 'date') { const v = parseDate(text); return isNaN(v) ? null : v; }
        if (type === 'wc') {
          const plus = text.endsWith('+') ? 0.5 : 0;
          const v = parseNum(text.replace('+', ''));
          return isNaN(v) ? null : v + plus;
        }
        return text.toLowerCase();
      }

      // Default sort: IPF GL Punkte (column index 10), descending.
      const DEFAULT_STATE = { col: 10, dir: 'desc' };

      // Track per-table state so we know when to re-apply (tbody-content fingerprint).
      let wiredTable = null;
      let tbodyObserver = null;
      let lastTbodySignature = null;
      let sorting = false;          // re-entry guard (synchronous)

      function getCurrentState() {
        const s = loadState();
        return s ? s : Object.assign({}, DEFAULT_STATE);
      }

      // Cheap signature of tbody content — set of (first-cell-text, name) pairs.
      function tbodySig(tbody) {
        if (!tbody) return null;
        const rows = tbody.querySelectorAll('tr');
        let sig = String(rows.length) + '|';
        // Use only a few rows + their name cell text — enough to detect filter changes.
        rows.forEach(function (r, i) { if (i < 8) sig += (r.children[1]?.textContent || '').slice(0,20) + ';'; });
        return sig;
      }

      function applySort(table, state) {
        if (sorting) return;
        const ths = table.querySelectorAll('thead tr:last-child th');
        const tbody = table.tBodies[0];
        if (!tbody || !ths[state.col]) return;
        const type = ths[state.col].dataset.sortType || 'text';
        const rows = Array.from(tbody.querySelectorAll('tr'));
        if (rows.length === 0) return;
        const dir = state.dir === 'desc' ? -1 : 1;
        rows.sort(function (a, b) {
          const qa = a.classList.contains('row--q') ? 1 : 0;
          const qb = b.classList.contains('row--q') ? 1 : 0;
          if (qa !== qb) return qb - qa;
          const va = valueOf(a, state.col, type);
          const vb = valueOf(b, state.col, type);
          if (va === null && vb === null) return 0;
          if (va === null) return 1;
          if (vb === null) return -1;
          if (va < vb) return -1 * dir;
          if (va > vb) return 1 * dir;
          return 0;
        });
        sorting = true;
        rows.forEach(function (r) { tbody.appendChild(r); });
        let n = 1;
        tbody.querySelectorAll('tr').forEach(function (r) {
          const rc = r.querySelector('td.rank');
          if (rc) rc.textContent = String(n++);
        });
        sorting = false;
        ths.forEach(function (h) {
          const a = h.querySelector('.sort-arrow');
          if (a) a.textContent = '↕';
          h.classList.remove('sort-active');
        });
        const active = ths[state.col];
        active.classList.add('sort-active');
        const arrow = active.querySelector('.sort-arrow');
        if (arrow) arrow.textContent = state.dir === 'asc' ? '↑' : '↓';
        lastTbodySignature = tbodySig(tbody);
      }

      function wireClickHandlers(table) {
        if (wiredTable === table) return;
        wiredTable = table;
        const ths = table.querySelectorAll('thead tr:last-child th');
        ths.forEach(function (th, idx) {
          if (th.classList.contains('nosort')) return;
          th.style.cursor = 'pointer';
          th.addEventListener('click', function () {
            const state = getCurrentState();
            const type = th.dataset.sortType || 'text';
            if (state.col === idx) {
              state.dir = state.dir === 'asc' ? 'desc' : 'asc';
            } else {
              state.col = idx;
              state.dir = (type === 'text') ? 'asc' : 'desc';
            }
            applySort(table, state);
            saveState(state);
          });
        });
      }

      function bindTbodyObserver(tbody) {
        if (tbodyObserver) tbodyObserver.disconnect();
        tbodyObserver = new MutationObserver(function () {
          if (sorting) return;
          const t = doc.getElementById('qual-table');
          if (!t) return;
          const sig = tbodySig(t.tBodies[0]);
          if (sig === lastTbodySignature) return;        // no real content change
          applySort(t, getCurrentState());
        });
        tbodyObserver.observe(tbody, { childList: true });
      }

      function syncSort() {
        const t = doc.getElementById('qual-table');
        if (!t) return false;
        wireClickHandlers(t);
        applySort(t, getCurrentState());
        const tb = t.tBodies[0];
        if (tb) bindTbodyObserver(tb);
        return true;
      }

      // Initial: keep polling lightly until the table exists, then stop polling.
      if (!syncSort()) {
        let tries = 0;
        const initId = setInterval(function () {
          if (syncSort() || ++tries > 30) clearInterval(initId);
        }, 150);
      }

      // Outer observer: only triggers when the table ELEMENT itself is replaced by a rerun.
      // Cheap: ignores nested DOM mutations entirely.
      const bodyObserver = new MutationObserver(function () {
        const t = doc.getElementById('qual-table');
        if (t && t !== wiredTable) {
          // New table instance — re-wire + re-sort.
          lastTbodySignature = null;
          syncSort();
        }
      });
      bodyObserver.observe(doc.body, { childList: true, subtree: true });
    })();
    </script>
            """,
            height=0,
        )
    else:
        st.info("Keine Athlet:innen im gewählten Filter gefunden.")

    # --- ZUSAMMENFASSUNGEN: Chart (Gewichtsklassen) + klickbare Vereine-Liste ---
    # Basis = alle Qualifizierten (Datum+Equipment+Event), unabhängig von Team/WC-Filter,
    # damit man die Verteilung sieht und per Klick filtern kann.
    if not selected_name and not best_baseline.empty:
        # Counts pro (Geschlecht, Gewichtsklasse)
        bl = best_baseline.assign(
            _wc=best_baseline["WeightClassKg"].apply(wc_display),
            _sx=best_baseline["Sex"].astype(str).str.upper(),
        )
        fem_counts = {wc: int(((bl["_sx"] == "F") & (bl["_wc"] == wc)).sum()) for wc in FEM_ORDER}
        mal_counts = {wc: int(((bl["_sx"] == "M") & (bl["_wc"] == wc)).sum()) for wc in MAL_ORDER}

        count_team = (
            best_baseline.groupby("Team").size().reset_index(name="n").sort_values("n", ascending=False)
        )

        # Chart "Qualifizierte pro Gewichtsklasse" nur zeigen, wenn keine Klassen gefiltert sind.
        show_wc_chart = not selected_wc
        if show_wc_chart:
            st.markdown(
                '<div class="section-head" style="margin-top:18px"><div>'
                '<div class="kicker kicker--gold">Verteilung</div>'
                '<h2>Qualifizierte pro Gewichtsklasse</h2></div>'
                f'<div class="meta">{int(best_baseline["Name"].nunique())} Athlet:innen gesamt</div></div>',
                unsafe_allow_html=True,
            )

        # --- Plotly-Chart (Frauen + Männer als Subplots, horizontale Balken) ---
        GOLD_W = "#E2C977"
        GOLD_M = "#E2C977"  # gleiche Farbe wie Frauen für visuelle Konsistenz
        max_count = max(list(fem_counts.values()) + list(mal_counts.values()) + [1])

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("FRAUEN", "MÄNNER"),
            horizontal_spacing=0.12,
            shared_xaxes=False,
        )
        # Damit "47" oben steht: y-Achse umkehren via autorange="reversed"
        FEM_LABELS = [wc_label(w) for w in FEM_ORDER]
        MAL_LABELS = [wc_label(w) for w in MAL_ORDER]
        fig.add_trace(
            go.Bar(
                y=FEM_LABELS,
                x=[fem_counts[w] for w in FEM_ORDER],
                orientation="h",
                marker=dict(color=GOLD_W, line=dict(color="#1F1F23", width=1)),
                text=[fem_counts[w] if fem_counts[w] else "" for w in FEM_ORDER],
                textposition="outside",
                textfont=dict(family="IBM Plex Mono", color=GOLD_W, size=13),
                hovertemplate="<b>%{y} kg</b><br>%{x} Athletinnen<extra></extra>",
                showlegend=False,
            ),
            row=1, col=1,
        )
        fig.add_trace(
            go.Bar(
                y=MAL_LABELS,
                x=[mal_counts[w] for w in MAL_ORDER],
                orientation="h",
                marker=dict(color=GOLD_M, line=dict(color="#1F1F23", width=1)),
                text=[mal_counts[w] if mal_counts[w] else "" for w in MAL_ORDER],
                textposition="outside",
                textfont=dict(family="IBM Plex Mono", color=GOLD_W, size=13),
                hovertemplate="<b>%{y} kg</b><br>%{x} Athleten<extra></extra>",
                showlegend=False,
            ),
            row=1, col=2,
        )
        # Wichtig: type="category" damit Plotly die Klassen als Strings rendert,
        # statt sie numerisch zu binnen ("45 kg, 50 kg, ...").
        fig.update_yaxes(
            type="category",
            autorange="reversed",
            categoryorder="array",
            categoryarray=FEM_LABELS + MAL_LABELS,
            tickfont=dict(family="IBM Plex Mono", size=12, color="#B6B6BB"),
            showgrid=False,
            ticksuffix=" kg",
        )
        fig.update_xaxes(showgrid=True, gridcolor="#2A2A30", zeroline=False,
                         tickfont=dict(family="IBM Plex Mono", size=11, color="#76767D"),
                         range=[0, max_count + max(1, max_count * 0.25)])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Archivo, sans-serif", color="#F5F5F4"),
            height=420,
            margin=dict(l=10, r=10, t=50, b=20),
            bargap=0.35,
        )
        for ann in fig["layout"]["annotations"]:
            ann["font"] = dict(family="IBM Plex Mono", size=11, color="#C9AE5B")
            ann["text"] = f"<b>{ann['text']}</b>"

        if show_wc_chart:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # --- Vereine (Goldbalken-Liste, reine Visualisierung) ---
        st.markdown(
            '<div class="section-head" style="margin-top:24px"><div>'
            '<div class="kicker kicker--gold">Vereine</div>'
            '<h2>Qualifizierte pro Verein</h2></div>'
            f'<div class="meta">{len(count_team)} Vereine vertreten</div></div>',
            unsafe_allow_html=True,
        )

        max_team = int(count_team["n"].max()) if not count_team.empty else 1
        team_rows_html = "".join(
            f'<a class="sumrow sumrow--link" href="?team={_urlquote(str(r.Team))}" target="_self">'
            f'<div class="sumrow__label">{esc(r.Team)}</div>'
            f'<div class="sumrow__bar"><i style="width:{r.n / max_team * 100:.0f}%"></i></div>'
            f'<div class="sumrow__num">{r.n}</div></a>'
            for r in count_team.itertuples()
        )
        st.markdown(
            f'<div class="sumcard">{team_rows_html}</div>',
            unsafe_allow_html=True,
        )


elif _page == "Rekorde":
    _records_df = load_records()
    # OeVK-Historie + EM/WM-Daten für österreichische Athlet:innen mergen
    _hist_full = load_full_history()
    _hist_intl = load_international_for_austrians()
    if not _hist_intl.empty and not _hist_full.empty:
        _hist_combined = pd.concat([_hist_full, _hist_intl], ignore_index=True)
    elif not _hist_intl.empty:
        _hist_combined = _hist_intl
    else:
        _hist_combined = _hist_full
    _bests_df = compute_dataset_bests(_hist_combined)

    # --- Section-Headline + CSV-Export (gleiche Optik wie im Qualifikation-Tab) ---
    _rec_hdr_left, _rec_hdr_right = st.columns([4, 1], vertical_alignment="center")
    with _rec_hdr_left:
        st.markdown(
            '<div class="section-head"><div>'
            '<h2>Österreichische Rekorde (Classic / Raw)</h2></div></div>',
            unsafe_allow_html=True,
        )
    with _rec_hdr_right:
        try:
            _rec_export_df = _records_df.copy()
            _rec_export_df.insert(0, "lift_de",
                _rec_export_df["lift"].map({"Total": "Total", "Squat": "Kniebeugen",
                                            "Bench": "Bankdrücken", "Deadlift": "Kreuzheben"}))
            _rec_csv_bytes = _rec_export_df.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                "⬇ CSV-Export",
                data=_rec_csv_bytes,
                file_name="oevk_rekorde.csv",
                mime="text/csv",
                key="dl_csv_rekorde",
                use_container_width=True,
            )
        except Exception:
            pass

    # --- Hilfe-Banner (kompakt) ---
    st.markdown(
        '<div class="rec-help">'
        '<span class="ico">ℹ</span>'
        '<div><b>OPL-Datensatz</b> = Vergleichswert aus OpenPowerlifting, kein offizieller '
        'Rekord. <span class="up">↑</span> = OPL-Wert über offiziellem Rekord.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # --- Filter: in der Sidebar (nur diese Seite) — Geschlecht / Gewichtsklasse / Altersklasse ---
    _rc_sex_pair = st.sidebar.selectbox(
        "Geschlecht",
        [("F", "Frauen"), ("M", "Männer")],
        index=None,
        format_func=lambda o: o[1],
        placeholder="Alle Geschlechter",
        key=f"rec_sex_v{_GEN_R}",
    )
    _rc_wc_pair = st.sidebar.selectbox(
        "Gewichtsklasse",
        WC_OPTIONS,
        index=None,
        format_func=_fmt_wc_option,
        placeholder="Alle Gewichtsklassen",
        key=f"rec_wc_v{_GEN_R}",
    )
    _rc_age = st.sidebar.selectbox(
        "Altersklasse",
        ["Jugend", "Junioren", "Open", "AK1", "AK2", "AK3", "AK4"],
        index=None,
        placeholder="Alle Altersklassen",
        key=f"rec_age_v{_GEN_R}",
    )
    st.sidebar.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
    if st.sidebar.button("↺ Filter zurücksetzen", key="reset_rec_btn"):
        _bump_gen("_gen_rec")

    _LIFT_EN2DE = {"Total": "Total", "Squat": "Kniebeugen",
                   "Bench": "Bankdrücken", "Deadlift": "Kreuzheben"}

    # Filter offizielle Rekorde (nur Raw — PDF enthält keine Single-ply-Daten)
    _off = _records_df[_records_df["equipment"] == "Raw"].copy()
    if _rc_wc_pair is not None:
        _sex_sel, _wc_sel = _rc_wc_pair
        _off = _off[(_off["sex"] == _sex_sel) & (_off["weight_class"] == _wc_sel)]
    if _rc_age:
        _off = _off[_off["age_class"] == _rc_age]
    if _rc_sex_pair is not None:
        _off = _off[_off["sex"] == _rc_sex_pair[0]]

    # Querystring-Suffix für Athleten-Profil-Links aus diesem Tab:
    # markiert "kam aus Rekorde-Tab" + aktuell gesetzten Filter — Profile-Back-Button kehrt damit hierher zurück.
    _rec_link_suffix = "&from=records"
    if _rc_wc_pair is not None:
        _rec_link_suffix += f"&rec_wc={_urlquote(_rc_wc_pair[0] + '-' + _rc_wc_pair[1])}"
    if _rc_age:
        _rec_link_suffix += f"&rec_ac={_urlquote(_rc_age)}"
    if _rc_sex_pair is not None:
        _rec_link_suffix += f"&rec_sex={_rc_sex_pair[0]}"
    _fqs_main = _filter_qs()
    if _fqs_main:
        _rec_link_suffix += "&" + _fqs_main

    # Sortier-Hilfen (feste, lesbare Reihenfolge — kein Klick-Sort mehr)
    _AGE_ORDER = {"Jugend": 0, "Junioren": 1, "Open": 2, "AK1": 3, "AK2": 4, "AK3": 5, "AK4": 6}
    _LIFT_ORDER = ["Total", "Squat", "Bench", "Deadlift"]   # Render-Reihenfolge der 4 Tabellen

    def _wc_key(s):
        s = str(s)
        return (1, 0.0) if s.endswith("+") else (0, float(s.replace("+", "") or 0))

    # OPL-Bestleistungen indexieren
    _bests_idx = (
        _bests_df.set_index(["sex", "age_class", "equipment", "weight_class", "lift"])
        if not _bests_df.empty else None
    )

    def _meet_cell(name, date_iso, cls_extra=""):
        if not name and not date_iso:
            return f'<td class="rec-meet rec-open{(" " + cls_extra) if cls_extra else ""}">–</td>'
        _nm = esc(str(name)) if name else "–"
        _wn = fmt_date(date_iso) if date_iso else ""
        _cls = ("rec-meet " + cls_extra).strip()
        return (f'<td class="{_cls}" title="{esc(str(name))}">'
                f'<span class="mname">{_nm}</span>'
                + (f'<span class="mwhen">{_wn}</span>' if _wn else '')
                + '</td>')

    def _opl_cells(sx, ac, wc, lift, has_official, off_kg):
        """Liefert (kg-Zelle, Athlet-Zelle, Wettkampf-Zelle) für die OPL-Spalten."""
        if _bests_idx is None:
            return ('<td class="num kg-opl rec-open opl-sep" data-label="OPL">–</td>',
                    '<td class="l rec-open" data-label="Athlet:in (OPL)">–</td>',
                    _meet_cell("", ""))
        _key = (sx, ac, "Raw", wc, lift)
        if _key not in _bests_idx.index:
            return ('<td class="num kg-opl rec-open opl-sep" data-label="OPL">–</td>',
                    '<td class="l rec-open" data-label="Athlet:in (OPL)">–</td>',
                    _meet_cell("", ""))
        _br = _bests_idx.loc[_key]
        if isinstance(_br, pd.DataFrame):
            _br = _br.iloc[0]
        _opl_kg = float(_br["kg"])
        _is_higher = has_official and off_kg is not None and _opl_kg > off_kg + 0.01
        _arrow = ' <span class="up">↑</span>' if _is_higher else ''
        _kg_cls = "num kg-opl opl-sep" + (" is-higher" if _is_higher else "")
        _kg = f'<td class="{_kg_cls}" data-label="OPL">{fmt_kg(_opl_kg)}{_arrow}</td>'
        _nm = str(_br["athlete"])
        _link = (f'<a class="nm-link" href="?athlete={_urlquote(_nm)}{_rec_link_suffix}" target="_self">{esc(_nm)}</a>')
        _name = f'<td class="l" data-label="Athlet:in (OPL)">{_link}</td>'
        return (_kg, _name, _meet_cell(_br["meet"], _br["date_iso"]))

    # Feste Spaltenbreiten — sorgen dafür, dass alle 4 Disziplin-Tabellen identisch ausgerichtet sind.
    _R_COLGROUP = (
        '<colgroup>'
        '<col style="width:78px">'    # Geschl.
        '<col style="width:118px">'   # Altersklasse
        '<col style="width:80px">'    # Gew.kl.
        '<col style="width:128px">'   # Offiz. Rekord
        '<col style="width:180px">'   # Athlet:in (offiziell)
        '<col style="width:240px">'   # Wettkampf (offiziell)
        '<col style="width:108px">'   # OPL
        '<col style="width:180px">'   # Athlet:in (OPL)
        '<col style="width:240px">'   # Wettkampf (OPL)
        '</colgroup>'
    )
    _R_HEAD = (
        _R_COLGROUP
        + '<thead><tr>'
        '<th>Geschl.</th><th>Altersklasse</th><th class="num">Gew.kl.</th>'
        '<th class="num">Offiz. Rekord</th><th class="l">Athlet:in (offiziell)</th>'
        '<th class="l">Wettkampf (offiziell)</th>'
        '<th class="num opl-sep">OPL</th><th class="l">Athlet:in (OPL)</th>'
        '<th class="l">Wettkampf (OPL)</th>'
        '</tr></thead>'
    )

    _any_rendered = False
    for _lift_en in _LIFT_ORDER:
        _lift_de = _LIFT_EN2DE[_lift_en]
        _sub = _off[_off["lift"] == _lift_en].copy()
        if _sub.empty:
            continue
        _sub = _sub.assign(
            _o_sex=_sub["sex"].map({"F": 0, "M": 1}).fillna(9),
            _o_age=_sub["age_class"].map(_AGE_ORDER).fillna(99),
            _o_wc=_sub["weight_class"].map(_wc_key),
        ).sort_values(["_o_sex", "_o_age", "_o_wc"])

        _rows = []
        for _, r in _sub.iterrows():
            _sx, _ac, _wc = r["sex"], r["age_class"], r["weight_class"]
            _tr_cls = ''
            _has_off = pd.notna(r["record_kg"])
            _off_kg = float(r["record_kg"]) if _has_off else None

            if _has_off:
                _kg_off = f'<td class="num kg-off" data-label="Offiz. Rekord">{fmt_kg(_off_kg)}</td>'
                _ath = str(r["athlete"])
                _ath_cell = (
                    f'<td class="l" data-label="Athlet:in (offiziell)">'
                    f'<a class="nm-link" href="?athlete={_urlquote(_ath)}{_rec_link_suffix}" target="_self">{esc(_ath)}</a></td>'
                    if _ath else '<td class="l rec-open" data-label="Athlet:in (offiziell)">–</td>'
                )
                _meet_off = _meet_cell(r["meet"], r["date_iso"])
            else:
                _kg_off = '<td class="num rec-open" data-label="Offiz. Rekord">Rekord offen</td>'
                _ath_cell = '<td class="l rec-open" data-label="Athlet:in (offiziell)">–</td>'
                _meet_off = _meet_cell("", "")

            _opl_kg, _opl_ath, _opl_meet = _opl_cells(_sx, _ac, _wc, _lift_en, _has_off, _off_kg)

            _rows.append(
                f'<tr{_tr_cls}>'
                f'<td data-label="Geschl."><span class="sex-tag">{sex_display(_sx)}</span></td>'
                f'<td class="mono" data-label="Altersklasse">{_ac}</td>'
                f'<td class="mono" data-label="Gew.kl.">{wc_label(_wc)}</td>'
                f'{_kg_off}{_ath_cell}{_meet_off}{_opl_kg}{_opl_ath}{_opl_meet}'
                f'</tr>'
            )

        st.markdown(
            f'<div class="section-head"><div><h2>{_lift_de}</h2></div></div>'
            f'<div class="tablecard"><div class="tablescroll">'
            f'<table class="tbl tbl-records">{_R_HEAD}<tbody>{"".join(_rows)}</tbody></table>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        _any_rendered = True

    if not _any_rendered:
        st.markdown('<div class="rec-empty">Keine Rekorde für diese Auswahl.</div>',
                    unsafe_allow_html=True)

    _stand = records_last_updated()
    _stand_str = _stand.strftime("%d.%m.%Y") if _stand else "—"
    st.markdown(
        f'<div class="rec-disclaimer">'
        f'<em><b>Quelle „Offiziell":</b> ÖVK-Rekordliste, Stand <b>{_stand_str}</b>, '
        f'veröffentlicht auf <a href="https://www.kraftdreikampf.at" target="_blank" rel="noopener" '
        f'style="color:var(--text-2)">www.kraftdreikampf.at</a>. '
        f'<b>Quelle „OPL":</b> berechnet aus dem '
        f'<a href="https://www.openpowerlifting.org" target="_blank" rel="noopener" '
        f'style="color:var(--text-2)">openpowerlifting.org</a>-Datensatz '
        f'(ausschließlich KDK-/3-Kampf-Wettkämpfe, inkl. EM/WM für österreichische Athlet:innen). '
        f'Die OPL-Werte können fehlerhaft oder unvollständig sein '
        f'(z.&nbsp;B. fehlende Meets, Tippfehler in Namen, falsche Klassen) – Abweichungen zur '
        f'offiziellen Liste dienen aktuell dem Abgleich, nicht der Übernahme.'
        f'</em></div>',
        unsafe_allow_html=True,
    )

# ============================================================
# === Bestenliste — Top-N nach IPF GL Points / Total kg ======
# ============================================================
elif _page == "Bestenliste":
    _hist_topn = load_full_history()

    # --- Filter: in der Sidebar (nur diese Seite) ---
    _topn_disc = st.sidebar.selectbox(
        "Disziplin",
        _DISC_OPTS,
        index=0,
        key=f"topn_disc_v{_GEN_T}",
    )
    _is_bench = _topn_disc.startswith("Bankdrücken")
    _bench_only_meets = (_topn_disc == "Bankdrücken (nur BD-Wettkämpfe)")

    _topn_sex_pair = st.sidebar.selectbox(
        "Geschlecht",
        [("F", "Frauen"), ("M", "Männer")],
        index=None,
        format_func=lambda o: o[1],
        placeholder="Alle Geschlechter",
        key=f"topn_sex_v{_GEN_T}",
    )
    _topn_wc_pair = st.sidebar.selectbox(
        "Gewichtsklasse",
        WC_OPTIONS,
        index=None,
        format_func=_fmt_wc_option,
        placeholder="Alle Gewichtsklassen",
        key=f"topn_wc_v{_GEN_T}",
    )
    _topn_age = st.sidebar.selectbox(
        "Altersklasse",
        ["Jugend", "Junioren", "Open", "AK1", "AK2", "AK3", "AK4"],
        index=None,
        placeholder="Alle Altersklassen",
        key=f"topn_age_v{_GEN_T}",
    )
    # Default 25 vor dem Widget setzen, damit kein Default+SessionState-Warning entsteht.
    if f"topn_n_v{_GEN_T}" not in st.session_state:
        st.session_state[f"topn_n_v{_GEN_T}"] = 25
    _topn_n = st.sidebar.number_input(
        "Anzahl",
        min_value=1,
        max_value=5000,
        step=5,
        key=f"topn_n_v{_GEN_T}",
    )
    st.sidebar.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
    if st.sidebar.button("↺ Filter zurücksetzen", key="reset_topn_btn"):
        _bump_gen("_gen_topn")

    # --- Header + CSV-Export ---
    _disc_title = "KDK · Total" if not _is_bench else (
        "Bankdrücken · nur BD-Wettkämpfe" if _bench_only_meets else "Bankdrücken · alle"
    )
    _topn_hdr_left, _topn_hdr_right = st.columns([4, 1], vertical_alignment="center")
    with _topn_hdr_left:
        st.markdown(
            f'<div class="section-head"><div>'
            f'<h2>Bestenliste · {_disc_title}</h2></div></div>',
            unsafe_allow_html=True,
        )

    # Hilfetext (kompakt, je Disziplin)
    if not _is_bench:
        _help = ('Beste Performance je Athlet:in (inkl. EM/WM), sortiert nach '
                 '<b>IPF GL Punkten</b>.')
    elif _bench_only_meets:
        _help = ('Bestes Bankdrücken aus <b>reinen Bankdrück-Wettkämpfen</b>, sortiert nach '
                 '<b>IPF GL Punkten</b> (Bankdrück-Variante).')
    else:
        _help = ('Bestes Bankdrücken je Athlet:in — aus KDK-Wettkämpfen UND reinen '
                 'Bankdrück-Wettkämpfen, sortiert nach <b>IPF GL Punkten</b> '
                 '(Bankdrück-Variante). Badge zeigt die Wettkampfart.')
    st.markdown(
        f'<div class="rec-help" style="margin-bottom:16px">'
        f'<span class="ico">ℹ</span><div>{_help}</div></div>',
        unsafe_allow_html=True,
    )

    # --- Datenaufbereitung ---
    if _hist_topn.empty:
        st.markdown('<div class="rec-empty">Keine Wettkampfdaten verfügbar.</div>',
                    unsafe_allow_html=True)
    else:
        _d = _hist_topn.copy()
        _d = _d[_d.get("Equipment", "").astype(str) == "Raw"]
        _d["bwkg"] = pd.to_numeric(_d.get("BodyweightKg"), errors="coerce")

        if not _is_bench:
            # KDK Total — nur 3-Kampf-Meets, Metrik = bestehende Total-GL
            _d = _d[_d.get("Event_Display", "").astype(str) == "KDK"]
            _d["perfkg"] = pd.to_numeric(_d.get("TotalKg"), errors="coerce")
            _d["glmetric"] = pd.to_numeric(_d.get("GL_Points"), errors="coerce")
        else:
            # Bankdrücken — Bank ist 2. Zahl in SBD; reine BD-Meets haben Event "Bankdrücken"
            if _bench_only_meets:
                _d = _d[_d.get("Event_Display", "").astype(str) == "Bankdrücken"]
            # sonst: alle Events (KDK + Bankdrücken) behalten
            _d["perfkg"] = pd.to_numeric(_d.get("Best3BenchKg"), errors="coerce")
            # Bench-GL via _gl_points_vec: Kopie mit Event=Bankdrücken & TotalKg=Bench
            _bcopy = _d.copy()
            _bcopy["Event_Display"] = "Bankdrücken"
            _bcopy["TotalKg"] = _d["perfkg"]
            _d["glmetric"] = pd.to_numeric(_gl_points_vec(_bcopy), errors="coerce")

        _d = _d[(_d["bwkg"] > 0) & (_d["perfkg"] > 0) & (_d["glmetric"] > 0)]

        # Cross-class Rollup für Altersklasse-Filter
        _AGE_ROLLUP_TOPN = {
            "Jugend":   ["Jugend"],
            "Junioren": ["Jugend", "Junioren"],
            "Open":     ["Jugend", "Junioren", "Open", "AK1", "AK2", "AK3", "AK4"],
            "AK1":      ["AK1"],
            "AK2":      ["AK2"],
            "AK3":      ["AK3"],
            "AK4":      ["AK4"],
        }
        if _topn_age:
            _allowed = _AGE_ROLLUP_TOPN.get(_topn_age, [_topn_age])
            _d = _d[_d.get("AgeClass").astype(str).isin(_allowed)]
        if _topn_sex_pair is not None:
            _d = _d[_d.get("Sex").astype(str).str.upper().str[:1] == _topn_sex_pair[0]]
        if _topn_wc_pair is not None:
            _sx_f, _wc_f = _topn_wc_pair
            _d = _d[(_d.get("Sex").astype(str).str.upper().str[:1] == _sx_f)
                    & (_d["WeightClassKg"].astype(str).map(wc_display) == _wc_f)]

        # Lifetime-Best pro Athlet:in nach der gewählten Metrik (GL)
        _d = _d.sort_values("glmetric", ascending=False).drop_duplicates("Name", keep="first")

        # --- Querystring-Suffix für Profil-Links ---
        _topn_link_suffix = "&from=topn"
        if _topn_disc and _topn_disc != _DISC_OPTS[0]:
            _topn_link_suffix += f"&topn_disc={_urlquote(_topn_disc)}"
        if _topn_sex_pair is not None:
            _topn_link_suffix += f"&topn_sex={_topn_sex_pair[0]}"
        if _topn_age:
            _topn_link_suffix += f"&topn_ac={_urlquote(_topn_age)}"
        if _topn_wc_pair is not None:
            _topn_link_suffix += f"&topn_wc={_urlquote(_topn_wc_pair[0] + '-' + _topn_wc_pair[1])}"
        if _topn_n:
            _topn_link_suffix += f"&topn_n={int(_topn_n)}"
        _fqs_topn = _filter_qs()
        if _fqs_topn:
            _topn_link_suffix += "&" + _fqs_topn

        # --- Tabelle: Spalten je Disziplin ---
        if not _is_bench:
            _T_COLGROUP = (
                '<colgroup>'
                '<col style="width:50px"><col style="width:220px"><col style="width:70px">'
                '<col style="width:60px"><col style="width:100px"><col style="width:80px">'
                '<col style="width:78px"><col style="width:160px"><col style="width:90px">'
                '<col style="width:108px"><col style="width:84px">'
                '<col style="width:200px"><col style="width:260px">'
                '</colgroup>'
            )
            _T_HEAD = (
                _T_COLGROUP + '<thead><tr>'
                '<th class="num">#</th><th class="l">Athlet:in</th><th>Geschl.</th>'
                '<th class="num">Alter</th><th>Altersklasse</th><th>Gew.kl.</th>'
                '<th class="num">BW</th><th class="num">SBD</th><th class="num">Total</th>'
                '<th class="num">IPF GL</th><th>Typ</th>'
                '<th class="l">Verein</th><th class="l">Wettkampf</th>'
                '</tr></thead>'
            )
        else:
            _T_COLGROUP = (
                '<colgroup>'
                '<col style="width:50px"><col style="width:220px"><col style="width:70px">'
                '<col style="width:60px"><col style="width:100px"><col style="width:80px">'
                '<col style="width:78px"><col style="width:110px"><col style="width:108px">'
                '<col style="width:84px"><col style="width:200px"><col style="width:260px">'
                '</colgroup>'
            )
            _T_HEAD = (
                _T_COLGROUP + '<thead><tr>'
                '<th class="num">#</th><th class="l">Athlet:in</th><th>Geschl.</th>'
                '<th class="num">Alter</th><th>Altersklasse</th><th>Gew.kl.</th>'
                '<th class="num">BW</th><th class="num">Bankdrücken</th>'
                '<th class="num">IPF GL</th><th>Typ</th>'
                '<th class="l">Verein</th><th class="l">Wettkampf</th>'
                '</tr></thead>'
            )

        def _meet_cell_html(r):
            _meet_name = esc(str(r.get("MeetName", "")))
            _meet_date = fmt_date(r.get("Date", ""))
            return (
                f'<td class="l rec-meet" title="{_meet_name}">'
                f'<span class="mname">{_meet_name}</span>'
                + (f'<span class="mwhen">{_meet_date}</span>' if _meet_date else '')
                + '</td>'
            )

        def _topn_row_html(rank, r):
            _nm = str(r.get("Name", ""))
            _link = (
                f'<a class="nm-link" href="?athlete={_urlquote(_nm)}{_topn_link_suffix}" '
                f'target="_self">{esc(_nm)}</a>'
            )
            _common = (
                f'<td class="num rank">{rank}</td>'
                f'<td class="cell-name l">{_link}</td>'
                f'<td><span class="sex-tag">{sex_display(r.get("Sex",""))}</span></td>'
                f'<td class="num mono">{fmt_age(r.get("Age"))}</td>'
                f'<td class="mono">{esc(str(r.get("AgeClass") or ""))}</td>'
                f'<td class="mono">{wc_label(r.get("WeightClassKg"))}</td>'
                f'<td class="num mono">{fmt_kg(r.get("BodyweightKg"), 2)}</td>'
            )
            if not _is_bench:
                _mid = (
                    f'<td class="num mono">{fmt_sbd(r.get("Best3SquatKg"), r.get("Best3BenchKg"), r.get("Best3DeadliftKg"))}</td>'
                    f'<td class="num mono-strong gold-strong">{fmt_kg(r.get("TotalKg"))}</td>'
                    f'<td class="num mono">{fmt_kg(r.get("glmetric"), 2)}</td>'
                    f'<td><span class="typ-tag kdk">KDK</span></td>'
                )
            else:
                _is_bd_meet = str(r.get("Event_Display", "")) == "Bankdrücken"
                _badge = ('<span class="typ-tag bd">BD-WK</span>' if _is_bd_meet
                          else '<span class="typ-tag kdk">KDK</span>')
                _mid = (
                    f'<td class="num mono-strong gold-strong">{fmt_kg(r.get("perfkg"))}</td>'
                    f'<td class="num mono">{fmt_kg(r.get("glmetric"), 2)}</td>'
                    f'<td>{_badge}</td>'
                )
            return (
                '<tr>' + _common + _mid
                + f'<td class="l">{esc(str(r.get("Team") or ""))}</td>'
                + _meet_cell_html(r) + '</tr>'
            )

        _d_top = _d.sort_values("glmetric", ascending=False).head(int(_topn_n))
        _topn_rows = [
            _topn_row_html(i, r._asdict())
            for i, r in enumerate(_d_top.itertuples(index=False), start=1)
        ]

        if not _topn_rows:
            st.markdown('<div class="rec-empty">Keine Performances für diese Auswahl.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="tablecard"><div class="tablescroll">'
                f'<table class="tbl tbl-records">{_T_HEAD}<tbody>{"".join(_topn_rows)}</tbody></table>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        # CSV-Export
        with _topn_hdr_right:
            if not _d.empty:
                try:
                    if not _is_bench:
                        _topn_export_cols = ["Name", "Sex", "Age", "AgeClass", "WeightClassKg",
                                             "BodyweightKg", "Best3SquatKg", "Best3BenchKg",
                                             "Best3DeadliftKg", "TotalKg", "GL_Points",
                                             "Team", "MeetName", "Date"]
                        _fname = "oevk_bestenliste_kdk.csv"
                    else:
                        _exp = _d.copy()
                        _exp["Bankdruecken_kg"] = _exp["perfkg"]
                        _exp["IPF_GL_Bench"] = _exp["glmetric"]
                        _exp["Wettkampftyp"] = _exp["Event_Display"].map(
                            lambda e: "BD-Wettkampf" if str(e) == "Bankdrücken" else "KDK")
                        _d = _exp
                        _topn_export_cols = ["Name", "Sex", "Age", "AgeClass", "WeightClassKg",
                                             "BodyweightKg", "Bankdruecken_kg", "IPF_GL_Bench",
                                             "Wettkampftyp", "Team", "MeetName", "Date"]
                        _fname = "oevk_bestenliste_bankdruecken.csv"
                    _existing_cols = [c for c in _topn_export_cols if c in _d.columns]
                    _topn_export_df = _d[_existing_cols].copy()
                    _csv_bytes = _topn_export_df.to_csv(index=False, sep=";",
                                                       encoding="utf-8-sig").encode("utf-8-sig")
                    st.download_button(
                        "⬇ CSV-Export",
                        data=_csv_bytes,
                        file_name=_fname,
                        mime="text/csv",
                        key="dl_csv_topn",
                        use_container_width=True,
                    )
                except Exception:
                    pass

elif _page == "Statistik":
    # ======================================================================
    # STATISTIK — Saison-Auswertung (KDK Raw, Qualifikationsfenster)
    # ======================================================================
    st.sidebar.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
    _stat_sex = st.sidebar.selectbox(
        "Geschlecht", ["Beide", "Frauen", "Männer"], key=f"stat_sex_v{_GEN_S}")
    if st.sidebar.button("Filter zurücksetzen", key=f"stat_reset_v{_GEN_S}",
                         use_container_width=True):
        _bump_gen("_gen_stat")

    _SEXES = {"Beide": ["F", "M"], "Frauen": ["F"], "Männer": ["M"]}[_stat_sex]
    _SEX_LABEL = {"F": "Frauen", "M": "Männer"}
    _WC_ORDER = {"F": FEM_ORDER, "M": MAL_ORDER}
    _SEX_COLOR = {"F": "#E2C977", "M": "#8FB8DE"}

    def _stat_head(title, meta=""):
        _m = f'<div class="meta">{meta}</div>' if meta else ""
        st.markdown(f'<div class="section-head" style="margin:22px 0 10px">'
                    f'<h2>{title}</h2>{_m}</div>', unsafe_allow_html=True)

    def _plot_theme(fig, height=340):
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=42, b=10), height=height,
            font=dict(family="Archivo, sans-serif", color="#F5F5F4", size=12),
            showlegend=False,
            hoverlabel=dict(bgcolor="#18181B", bordercolor="#C9AE5B", font_color="#F5F5F4"),
        )
        fig.update_xaxes(gridcolor="#26262B", zerolinecolor="#26262B")
        fig.update_yaxes(gridcolor="#26262B", zerolinecolor="#26262B")
        return fig

    def _tbl(headers, rows_html, extra_cls=""):
        _h = "".join(f'<th class="{c}">{t}</th>' for t, c in headers)
        st.markdown(
            f'<div class="tablecard"><div class="tablescroll">'
            f'<table class="tbl {extra_cls}"><thead><tr>{_h}</tr></thead>'
            f'<tbody>{rows_html}</tbody></table></div></div>',
            unsafe_allow_html=True)

    def _subhead(label):
        # Untertitel im Stil der Tabellen-Kopfzeile (Mono, fett, größer)
        st.markdown(
            f'<div style="font-family:var(--font-mono);font-size:15px;font-weight:700;'
            f'letter-spacing:0.12em;text-transform:uppercase;color:var(--gold-bright);'
            f'margin:16px 0 8px">{label}</div>', unsafe_allow_html=True)

    # ---------- Datenbasis ----------
    _pool_all = df_scope.copy()
    for _c in ("TotalKg", "BodyweightKg", "GL_Points", "Differenz"):
        if _c in _pool_all.columns:
            _pool_all[_c] = pd.to_numeric(_pool_all[_c], errors="coerce")
    _pool_all["_sx"] = _pool_all["Sex"].astype(str).str.upper().str[:1]
    _pool = (_pool_all.sort_values("TotalKg", ascending=False)
             .drop_duplicates("Name").copy())
    _pool = _pool[_pool["_sx"].isin(_SEXES)]

    st.markdown('<div class="section-head"><h2>Statistik</h2>'
                '<div class="meta">KDK Raw · Saison 2025/26</div></div>',
                unsafe_allow_html=True)
    st.markdown(
        '<p style="color:var(--text-2);font-size:13.5px;margin:6px 0 4px;max-width:820px">'
        'Auswertung aller gewerteten KDK-Raw-Leistungen im Qualifikationsfenster '
        f'({QUAL_WINDOW_START.strftime("%d.%m.%Y")} – '
        f'{(QUAL_WINDOW_END - pd.Timedelta(days=1)).strftime("%d.%m.%Y")}), '
        'eine (beste) Leistung je Athlet:in.</p>',
        unsafe_allow_html=True)

    if _pool.empty:
        st.info("Keine Daten im gewählten Bereich.")
    else:
        # ================= 1 · Feld-Überblick (KPIs) =================
        _n_ath = int(_pool["Name"].nunique())
        _n_qual = int(_pool["Qualifiziert"].sum()) if "Qualifiziert" in _pool.columns \
            else int((_pool["Differenz"] >= 0).sum())
        _quote = (_n_qual / _n_ath * 100) if _n_ath else 0.0
        _n_classes = int(_pool.groupby(["_sx", "_wc_disp"]).ngroups)
        _n_meets = int(_pool_all[_pool_all["_sx"].isin(_SEXES)]["MeetName"].nunique())
        _nf = int(_pool[_pool["_sx"] == "F"]["Name"].nunique())
        _nm = int(_pool[_pool["_sx"] == "M"]["Name"].nunique())
        st.markdown(
            '<div class="kpis" style="grid-template-columns:repeat(2,1fr)">'
            + kpi_card("Athlet:innen", _n_ath, accent=True, foot=f"{_nf} Frauen · {_nm} Männer")
            + kpi_card("Qualifiziert", _n_qual, foot=f"{_quote:.0f}% des Feldes · {_n_meets} Wettkämpfe")
            + "</div>",
            unsafe_allow_html=True)

        # ================= 2 · Qualifikationsnorm im Vergleich (neutral) =================
        def _ceiling_bw(wc):
            return float(wc[:-1]) if wc.endswith("+") else float(wc)

        _norm_rows = []
        for _sx in _SEXES:
            for _wc in _WC_ORDER[_sx]:
                _norm = _QUAL_FLAT.get((_sx, _wc))
                if _norm is None:
                    continue
                _sub = _pool[(_pool["_sx"] == _sx) & (_pool["_wc_disp"] == _wc)]
                _n = len(_sub)
                _bw_med = float(_sub["BodyweightKg"].median()) if _n else float("nan")
                if _n and not np.isnan(_bw_med):
                    _ref_bw, _approx = _bw_med, False
                else:
                    _ref_bw, _approx = _ceiling_bw(_wc), True
                _gl_norm = _gl_of(_sx, _norm, _ref_bw)
                _nq = int((_sub["TotalKg"] >= _norm).sum()) if _n else 0
                _rate = (_nq / _n * 100) if _n else float("nan")
                _mratio = float((_sub["TotalKg"] / _norm).median() * 100) if _n else float("nan")
                _norm_rows.append(dict(sex=_sx, wc=_wc, norm=_norm, ref_bw=_ref_bw,
                                       approx=_approx, gl=_gl_norm, n=_n, nq=_nq,
                                       rate=_rate, mratio=_mratio))
        _norm_df = pd.DataFrame(_norm_rows)

        _stat_head("Qualifikationsnorm im Vergleich",
                   "IPF-GL-Äquivalent je Klasse")
        st.markdown(
            '<p style="color:var(--text-2);font-size:13px;margin:0 0 10px;max-width:860px">'
            'Norm jeder Klasse in GL-Punkte.</p>',
            unsafe_allow_html=True)

        def _bars_by_sex(val_key, height=340, pct=False):
            _cols = len(_SEXES)
            fig = make_subplots(rows=1, cols=_cols, shared_yaxes=False,
                                subplot_titles=[_SEX_LABEL[s] for s in _SEXES],
                                horizontal_spacing=0.18)
            for i, _sx in enumerate(_SEXES, start=1):
                d = _norm_df[_norm_df["sex"] == _sx]
                if d.empty:
                    continue
                ys = [wc_label(w) for w in d["wc"]]
                xs = [None if pd.isna(v) else float(v) for v in d[val_key]]
                txt = ["–" if v is None else (f"{v:.0f}%" if pct else f"{v:.1f}") for v in xs]
                fig.add_trace(go.Bar(
                    y=ys, x=xs, orientation="h",
                    marker=dict(color=_SEX_COLOR[_sx]),
                    text=txt, textposition="auto",
                    hovertemplate="%{y}: %{x:.1f}" + ("%" if pct else "") + "<extra></extra>",
                ), row=1, col=i)
                _vals = [v for v in xs if v is not None]
                if _vals:
                    _mean = sum(_vals) / len(_vals)
                    fig.add_vline(x=_mean, line=dict(color="#C9AE5B", width=1, dash="dash"),
                                  row=1, col=i)
                fig.update_yaxes(categoryorder="array",
                                 categoryarray=[wc_label(w) for w in _WC_ORDER[_sx]],
                                 autorange="reversed", row=1, col=i)
            return _plot_theme(fig, height)

        _fig_gl = _bars_by_sex("gl", height=360)
        _fig_gl.update_xaxes(title_text="Norm in IPF-GL-Punkten")
        st.plotly_chart(_fig_gl, use_container_width=True, config={"displayModeBar": False})

        # ---- Körpergewicht vs. Total (Graph über den Tabellen) ----
        _stat_head("Körpergewicht vs. Total",
                   "Punkt = eine Athlet:in · Linie = Durchschnitt je Geschlecht")
        _figs = go.Figure()
        for _sx in _SEXES:
            d = _pool[(_pool["_sx"] == _sx)
                      & (pd.to_numeric(_pool["TotalKg"], errors="coerce") > 0)]
            if d.empty:
                continue
            _q = d["Qualifiziert"] == True if "Qualifiziert" in d.columns else (d["Differenz"] >= 0)
            _figs.add_trace(go.Scatter(
                x=d["BodyweightKg"], y=d["TotalKg"], mode="markers",
                name=_SEX_LABEL[_sx],
                marker=dict(size=8, color=_SEX_COLOR[_sx],
                            line=dict(width=[1.4 if q else 0 for q in _q],
                                      color="#0B0B0C")),
                customdata=list(zip(d["Name"], [wc_label(w) for w in d["_wc_disp"]],
                                    d["GL_Points"])),
                hovertemplate="<b>%{customdata[0]}</b> · %{customdata[1]}<br>"
                              "BW %{x:.1f} · Total %{y:.1f} · GL %{customdata[2]:.1f}<extra></extra>",
            ))
            # Trend-/Durchschnittslinie (lineare Regression) je Geschlecht
            _bwv = pd.to_numeric(d["BodyweightKg"], errors="coerce")
            _tov = pd.to_numeric(d["TotalKg"], errors="coerce")
            _ok = _bwv.notna() & _tov.notna()
            if _ok.sum() >= 3:
                _m, _b = np.polyfit(_bwv[_ok], _tov[_ok], 1)
                _x0, _x1 = float(_bwv[_ok].min()), float(_bwv[_ok].max())
                _figs.add_trace(go.Scatter(
                    x=[_x0, _x1], y=[_m * _x0 + _b, _m * _x1 + _b],
                    mode="lines", name=f"Ø {_SEX_LABEL[_sx]}",
                    line=dict(color=_SEX_COLOR[_sx], width=2.5, dash="dash"),
                    hovertemplate="Ø " + _SEX_LABEL[_sx] + ": BW %{x:.0f} → ~%{y:.0f} kg<extra></extra>",
                ))
        _plot_theme(_figs, height=840)
        _figs.update_layout(showlegend=True,
                            legend=dict(orientation="h", y=1.06, x=0,
                                        font=dict(color="#B6B6BB")))
        _figs.update_xaxes(title_text="Körpergewicht [kg]")
        _figs.update_yaxes(title_text="Total [kg]")
        st.plotly_chart(_figs, use_container_width=True, config={"displayModeBar": False})

        # Norm-Tabellen je Geschlecht getrennt
        for _sx in _SEXES:
            d = _norm_df[_norm_df["sex"] == _sx]
            if d.empty:
                continue
            _nrow = []
            for r in d.itertuples():
                _refbw = "–" if pd.isna(r.ref_bw) else (fmt_kg(r.ref_bw, 1) + ("*" if r.approx else ""))
                _glc = "–" if pd.isna(r.gl) else fmt_kg(r.gl, 1)
                _mrc = "–" if pd.isna(r.mratio) else f"{r.mratio:.0f}%"
                _nrow.append(
                    f'<tr><td>{wc_label(r.wc)}</td>'
                    f'<td class="num mono">{fmt_kg(r.norm)}</td>'
                    f'<td class="num mono">{_refbw}</td>'
                    f'<td class="num gold-strong">{_glc}</td>'
                    f'<td class="num mono">{_mrc}</td></tr>')
            _subhead(_SEX_LABEL[_sx])
            _tbl([("Klasse", ""), ("Norm (kg)", "num"), ("Ref-KG", "num"),
                  ("Norm in GL", "num"), ("Median Total/Norm", "num")],
                 "".join(_nrow))
        st.markdown(
            '<p style="color:var(--text-3);font-size:11.5px;margin:-14px 0 2px;max-width:860px">'
            'Basis: KDK Raw, je (Geschlecht, Klasse) — ohne Altersklassen-Differenzierung. '
            'IPF-GL ist ein Modell zum Körpergewichts-Ausgleich. '
            '* Referenzgewicht geschätzt (keine bzw. offene Klasse).</p>',
            unsafe_allow_html=True)

        # ================= 3 · IPF GL Punkte je Klasse =================
        _stat_head("IPF GL Punkte je Klasse", "Was es in dieser Saison brauchte")
        for _sx in _SEXES:
            _srows = []
            for _wc in _WC_ORDER[_sx]:
                _sub = _pool[(_pool["_sx"] == _sx) & (_pool["_wc_disp"] == _wc)]
                _n = len(_sub)
                if _n == 0:
                    continue
                _gl = _sub["GL_Points"].dropna()
                _tot = _sub["TotalKg"].dropna()
                _med_gl = _gl.median() if not _gl.empty else float("nan")
                _p90_gl = _gl.quantile(0.90) if not _gl.empty else float("nan")
                _max_gl = _gl.max() if not _gl.empty else float("nan")
                _med_tot = _tot.median() if not _tot.empty else float("nan")
                _srows.append(
                    f'<tr><td>{wc_label(_wc)}</td>'
                    f'<td class="num mono">{_n}</td>'
                    f'<td class="num mono">{fmt_kg(_med_gl, 1)}</td>'
                    f'<td class="num mono">{fmt_kg(_p90_gl, 1)}</td>'
                    f'<td class="num gold-strong">{fmt_kg(_max_gl, 1)}</td>'
                    f'<td class="num mono">{fmt_kg(_med_tot)}</td></tr>')
            if _srows:
                _subhead(_SEX_LABEL[_sx])
                _tbl([("Klasse", ""), ("n", "num"), ("Median GL", "num"),
                      ("Top-10 % GL", "num"), ("Bester GL", "num"),
                      ("Median Total", "num")],
                     "".join(_srows))

        # ================= 4 · Feldgröße & Qualifizierte =================
        _stat_head("Feldgröße & Qualifizierte je Klasse",
                   "dunkler Balken = Starts · farbiger Balken = qualifiziert")
        _figd = make_subplots(rows=1, cols=len(_SEXES), shared_yaxes=False,
                              subplot_titles=[_SEX_LABEL[s] for s in _SEXES],
                              horizontal_spacing=0.18)
        for i, _sx in enumerate(_SEXES, start=1):
            dd = _norm_df[_norm_df["sex"] == _sx]
            if dd.empty:
                continue
            ys = [wc_label(w) for w in dd["wc"]]
            _figd.add_trace(go.Bar(
                y=ys, x=dd["n"].tolist(), orientation="h", name="Starts",
                marker=dict(color="#3A3A42"), showlegend=(i == 1), legendgroup="starts",
                hovertemplate="%{y}: %{x} Starts<extra></extra>"), row=1, col=i)
            _figd.add_trace(go.Bar(
                y=ys, x=dd["nq"].tolist(), orientation="h", name="Qualifiziert",
                marker=dict(color=_SEX_COLOR[_sx]), showlegend=False,
                text=dd["nq"].tolist(), textposition="inside", insidetextanchor="middle",
                hovertemplate="%{y}: %{x} qualifiziert<extra></extra>"), row=1, col=i)
            _figd.update_yaxes(categoryorder="array",
                               categoryarray=[wc_label(w) for w in _WC_ORDER[_sx]],
                               autorange="reversed", row=1, col=i)
        _plot_theme(_figd, height=380)
        _figd.update_layout(barmode="overlay", showlegend=True,
                            legend=dict(orientation="h", y=1.08, x=0,
                                        font=dict(color="#B6B6BB")))
        _figd.update_traces(opacity=0.95)
        st.plotly_chart(_figd, use_container_width=True, config={"displayModeBar": False})

        for _sx in _SEXES:
            d = _norm_df[_norm_df["sex"] == _sx]
            if d.empty:
                continue
            _frow = []
            for r in d.itertuples():
                _ratec = "–" if pd.isna(r.rate) else f"{r.rate:.0f}%"
                _frow.append(
                    f'<tr><td>{wc_label(r.wc)}</td>'
                    f'<td class="num mono">{r.n}</td>'
                    f'<td class="num mono">{r.nq}</td>'
                    f'<td class="num mono">{_ratec}</td></tr>')
            _subhead(_SEX_LABEL[_sx])
            _tbl([("Klasse", ""), ("Feld", "num"), ("Qualifiziert", "num"), ("Quote", "num")],
                 "".join(_frow))

        # ================= 5 · Vereinsranking =================
        _stat_head("Vereinsranking", "Beste Leistung je Athlet:in")
        _team = _pool.copy()
        _team["Team"] = _team["Team"].astype(str)
        _team = _team[_team["Team"].str.strip().ne("") & _team["Team"].str.lower().ne("nan")]
        if _team.empty:
            st.markdown('<p style="color:var(--text-3);font-size:12px">Keine Vereinsdaten.</p>',
                        unsafe_allow_html=True)
        else:
            _team["_q"] = (_team["Qualifiziert"] == True) if "Qualifiziert" in _team.columns \
                else (_team["Differenz"] >= 0)
            _agg = _team.groupby("Team").agg(
                ath=("Name", "nunique"), qual=("_q", "sum"),
                avg_gl=("GL_Points", "mean"), med_gl=("GL_Points", "median"),
                best_gl=("GL_Points", "max"),
            ).reset_index().sort_values(["qual", "avg_gl"], ascending=[False, False])
            _vrows = []
            for i, r in enumerate(_agg.itertuples(), start=1):
                _quote = (r.qual / r.ath * 100) if r.ath else 0
                _vrows.append(
                    f'<tr><td class="num mono">{i}</td>'
                    f'<td class="l">{esc(r.Team)}</td>'
                    f'<td class="num mono">{int(r.ath)}</td>'
                    f'<td class="num mono">{int(r.qual)}</td>'
                    f'<td class="num mono">{_quote:.0f}%</td>'
                    f'<td class="num mono">{fmt_kg(r.avg_gl, 1)}</td>'
                    f'<td class="num mono">{fmt_kg(r.med_gl, 1)}</td>'
                    f'<td class="num gold-strong">{fmt_kg(r.best_gl, 1)}</td></tr>')
            _tbl([("#", "num"), ("Verein", "l"), ("Athlet:innen", "num"),
                  ("Qualifiziert", "num"), ("Quote", "num"), ("Ø IPF-GL", "num"),
                  ("Median IPF-GL", "num"), ("Bester GL", "num")],
                 "".join(_vrows))

        # ================= 6 · Saisonverlauf =================
        _stat_head("Saisonverlauf", "Aktivität je Monat im Qualifikationsfenster")
        _ts = _pool_all[_pool_all["_sx"].isin(_SEXES)].copy()
        _ts["_dt"] = pd.to_datetime(_ts["Date"], errors="coerce")
        _ts = _ts.dropna(subset=["_dt"])
        if _ts.empty:
            st.markdown('<p style="color:var(--text-3);font-size:12px">Keine Zeitdaten.</p>',
                        unsafe_allow_html=True)
        else:
            _ts["_ym"] = _ts["_dt"].dt.to_period("M").astype(str)   # 'YYYY-MM'
            _ts["_qe"] = (pd.to_numeric(_ts["TotalKg"], errors="coerce")
                          >= pd.to_numeric(_ts["smLimit"], errors="coerce"))
            # "Neu qualifiziert" auf denselben qualifizierten Athlet:innen-Satz wie die
            # KPI stützen (beste Leistung je Athlet:in), damit die Summe konsistent bleibt.
            _qual_names = (set(_pool.loc[_pool["Qualifiziert"] == True, "Name"])
                           if "Qualifiziert" in _pool.columns
                           else set(_pool.loc[_pool["Differenz"] >= 0, "Name"]))
            _newq = (_ts[_ts["_qe"] & _ts["Name"].isin(_qual_names)]
                     .sort_values("_dt").groupby("Name")["_ym"].first().value_counts())

            def _mlabel(ym):
                y, m = ym.split("-")
                return f"{m}.{y}"

            _months = sorted(_ts["_ym"].unique())
            _labels, _starts, _trows = [], [], []
            for ym in _months:
                sub = _ts[_ts["_ym"] == ym]
                _mnames = sorted(str(m) for m in sub["MeetName"].dropna().unique())
                meets = len(_mnames)
                starts = int(len(sub))
                aths = int(sub["Name"].nunique())
                nq = int(_newq.get(ym, 0))
                _labels.append(_mlabel(ym))
                _starts.append(starts)
                _trows.append(
                    f'<tr><td class="l">{_mlabel(ym)}</td>'
                    f'<td class="num mono">{meets}</td>'
                    f'<td class="num mono">{starts}</td>'
                    f'<td class="num mono">{aths}</td>'
                    f'<td class="num gold-strong">{nq}</td>'
                    f'<td class="l" style="white-space:normal">{esc(" · ".join(_mnames))}</td></tr>')
            _figt = go.Figure()
            _figt.add_trace(go.Bar(
                x=_labels, y=_starts, marker=dict(color="#E2C977"),
                text=_starts, textposition="auto",
                hovertemplate="%{x}: %{y} Starts<extra></extra>"))
            _plot_theme(_figt, height=300)
            _figt.update_xaxes(categoryorder="array", categoryarray=_labels)
            _figt.update_yaxes(title_text="Starts")
            st.plotly_chart(_figt, use_container_width=True, config={"displayModeBar": False})
            _tbl([("Monat", "l"), ("Wettkämpfe", "num"), ("Starts", "num"),
                  ("Athlet:innen", "num"), ("Neu qualifiziert", "num"), ("Wettkämpfe (Namen)", "l")],
                 "".join(_trows))

# --- Credits / Datenquelle ---
st.markdown(
    '<div class="credit">Basiert auf Daten von '
    '<a href="https://www.openpowerlifting.org" target="_blank" rel="noopener">openpowerlifting.org</a> · '
    'OpenIPF-Distribution: <a href="https://www.openipf.org" target="_blank" rel="noopener">openipf.org</a></div>',
    unsafe_allow_html=True,
)
