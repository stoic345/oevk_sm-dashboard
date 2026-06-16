import streamlit as st
import streamlit.components.v1 as _components
import pandas as pd
import numpy as np
import base64
import html as _html
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

/* Streamlit chrome — Header bleibt sichtbar (enthält den Sidebar-Expand-Button!).
   Wir machen ihn nur transparent + entfernen Menü/Footer. */
#MainMenu, footer {visibility:hidden; height:0;}
header[data-testid="stHeader"] { background:transparent !important; }
header[data-testid="stHeader"] [data-testid="stToolbar"],
header[data-testid="stHeader"] [data-testid="stMainMenu"],
header[data-testid="stHeader"] [data-testid="stStatusWidget"] { display:none !important; }
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
[data-testid="stSidebar"] [data-baseweb="select"] > div, [data-testid="stSidebar"] input {
  background:var(--bg-elev) !important; border-color:var(--line) !important; }

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
.status-pill { display:flex; align-items:center; justify-content:center; gap:10px;
  background:var(--bg-elev); border:1px solid var(--gold-dim); border-radius:var(--r-sm);
  padding:10px 14px; font-family:var(--font-mono); font-size:12px; line-height:1.2;
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
.kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:0; }
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
.section-head h2 { font-family:var(--font-body); font-size:26px; font-weight:700; letter-spacing:-0.01em; margin:0; }
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
/* Streamlit Cloud "View source on GitHub"-Badge + Toolbar verstecken.
   WICHTIG: NIEMALS header[data-testid="stHeader"] hier hinzufügen — der enthält den
   Sidebar-Expand-Button (»). */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
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
  padding-top: 1rem !important;
}
[data-testid="stMain"] [data-testid="stVerticalBlock"] {
  gap: 28px !important;
}
/* st.markdown-Wrapper um eingebettete Style-Tags visuell unsichtbar machen
   (verhindert Vertical Jump bei conditional CSS-Injection). */
[data-testid="stMarkdown"]:has(> [data-testid="stMarkdownContainer"] > style:only-child),
[data-testid="stMarkdown"]:has(style:only-child) {
  margin:0 !important; padding:0 !important; min-height:0 !important; height:0 !important;
  display:none !important;
}
/* Sidebar — Default: 296 px Expanded. Folded-State wird via Python conditional CSS gesetzt. */
[data-testid="stSidebar"], section[data-testid="stSidebar"], aside[data-testid="stSidebar"] {
  display:block !important; visibility:visible !important; opacity:1 !important;
  transform:none !important; margin-left:0 !important;
  min-width:296px !important; width:296px !important; max-width:296px !important;
  transition: min-width .25s ease, width .25s ease, max-width .25s ease !important;
}
[data-testid="stSidebar"] > div:first-child {
  min-width:296px !important; width:296px !important;
}
/* Sidebar-Header bündig nach oben — kein Default-Padding */
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
  padding-top:8px !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] { padding:0 !important; height:0 !important; }

/* Toggle-Button (sb_toggle_btn) — Goldpille, oben rechts. Adressiert via key-Klasse. */
.st-key-sb_toggle_btn { margin:0 0 8px 0 !important; padding:0 !important; }
.st-key-sb_toggle_btn [data-testid="stButton"] {
  display:flex !important; justify-content:flex-end !important; width:100% !important;
}
body.sb-folded .st-key-sb_toggle_btn [data-testid="stButton"] {
  justify-content:center !important;
}
[data-testid="stSidebar"] .st-key-sb_toggle_btn [data-testid="stButton"] button {
  background:linear-gradient(180deg, var(--gold-bright) 0%, var(--gold) 100%) !important;
  border:1px solid var(--gold-bright) !important; border-radius:50% !important;
  color:#0B0B0C !important; font-family:var(--font-mono) !important; font-size:20px !important;
  font-weight:700 !important; line-height:1 !important; letter-spacing:0 !important;
  width:42px !important; min-width:42px !important; min-height:42px !important; height:42px !important;
  padding:0 !important; margin:0 !important; text-transform:none !important;
  box-shadow:0 4px 14px rgba(201,174,91,0.45), inset 0 1px 0 rgba(255,255,255,0.35) !important;
  transition:transform .15s ease, box-shadow .15s ease, filter .15s ease !important;
}
[data-testid="stSidebar"] .st-key-sb_toggle_btn [data-testid="stButton"] button:hover {
  filter:brightness(1.10) !important; transform:scale(1.06);
  box-shadow:0 6px 22px rgba(201,174,91,0.6), inset 0 1px 0 rgba(255,255,255,0.45) !important;
  background:linear-gradient(180deg, var(--gold-bright) 0%, var(--gold) 100%) !important;
  color:#0B0B0C !important; border-color:var(--gold-bright) !important;
}
[data-testid="stSidebar"] .st-key-sb_toggle_btn [data-testid="stButton"] button:focus,
[data-testid="stSidebar"] .st-key-sb_toggle_btn [data-testid="stButton"] button:focus-visible,
[data-testid="stSidebar"] .st-key-sb_toggle_btn [data-testid="stButton"] button:active {
  background:linear-gradient(180deg, var(--gold-bright) 0%, var(--gold) 100%) !important;
  border:1px solid var(--gold-bright) !important; color:#0B0B0C !important;
  box-shadow:0 4px 14px rgba(201,174,91,0.45), inset 0 1px 0 rgba(255,255,255,0.35) !important;
  outline:none !important;
}
[data-testid="stSidebar"] .st-key-sb_toggle_btn [data-testid="stButton"] button:active { transform:scale(0.96); }
[data-testid="stSidebar"] .st-key-sb_toggle_btn [data-testid="stButton"] button p,
[data-testid="stSidebar"] .st-key-sb_toggle_btn [data-testid="stButton"] button span,
[data-testid="stSidebar"] .st-key-sb_toggle_btn [data-testid="stButton"] button div {
  margin:0 !important; line-height:1 !important; color:#0B0B0C !important; font-size:20px !important;
}
/* Streamlits eigene Collapse/Expand-Knöpfe verstecken — wir steuern den Fold selbst */
[data-testid="stSidebarCollapseButton"],
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
  display:none !important; visibility:hidden !important;
}
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
.profile-meta { display:flex; gap:24px; color:var(--text-2); font-family:var(--font-mono); font-size:12px;
  letter-spacing:0.08em; text-transform:uppercase; margin:2px 0 18px; flex-wrap:wrap; }
.profile-meta .v { color:var(--text); margin-left:6px; }
.disc-grid { display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:14px; margin-bottom:18px; }
@media (max-width: 900px) { .disc-grid { grid-template-columns:1fr; } }
.disc-tile { background:var(--bg-elev); border:1px solid var(--line); border-radius:var(--r-md);
  padding:14px 16px; transition:border-color .14s ease, opacity .14s ease; }
.disc-tile:hover { border-color:var(--gold-dim); }
.disc-tile.empty { opacity:0.45; }
.disc-tile .kicker { font-family:var(--font-mono); font-size:11px; letter-spacing:0.18em;
  text-transform:uppercase; color:var(--gold); font-weight:600; margin-bottom:10px; }
.disc-tile .row { display:flex; justify-content:space-between; align-items:baseline; gap:10px;
  padding:4px 0; border-bottom:1px solid var(--line-soft); }
.disc-tile .row:last-of-type { border-bottom:none; }
.disc-tile .lab { font-family:var(--font-mono); font-size:11px; letter-spacing:0.10em;
  text-transform:uppercase; color:var(--text-3); }
.disc-tile .val { font-family:var(--font-mono); font-weight:600; font-size:17px;
  color:var(--gold-bright); font-variant-numeric:tabular-nums; }
.disc-tile .foot { margin-top:8px; font-family:var(--font-mono); font-size:10px; letter-spacing:0.08em;
  text-transform:uppercase; color:var(--text-3); }
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
  .target { display:none; } .kpi__value { font-size:30px; } }

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

/* Multiselect / Selectbox controls */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background:var(--bg-elev) !important; border:1px solid var(--line) !important;
  border-radius:var(--r-sm) !important; min-height:42px;
  transition:border-color .12s ease;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
  border-color:var(--gold-dim) !important;
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
  .target { display:none !important; }

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

  /* --- Tabelle → Karten-Layout --- */
  table.tbl thead { display:none !important; }
  .tablescroll { overflow-x:visible !important; }
  table.tbl, table.tbl tbody, table.tbl tr, table.tbl td { display:block !important; width:100% !important; }
  table.tbl tr {
    border:1px solid var(--line) !important; border-radius:var(--r-md) !important;
    margin:0 0 12px 0 !important; padding:12px 14px !important; background:var(--surface) !important;
  }
  table.tbl tr.row--q { border-left:3px solid var(--green) !important; }
  table.tbl tr.row--w { border-left:3px solid var(--amber) !important; }
  table.tbl tbody tr:hover td { background:transparent !important; }
  table.tbl td {
    display:flex !important; justify-content:space-between !important; align-items:center !important;
    gap:14px !important; padding:5px 0 !important; border:none !important;
    text-align:right !important; white-space:normal !important; box-shadow:none !important;
  }
  table.tbl td::before {
    content:attr(data-label); color:var(--text-3); font-family:var(--font-mono);
    font-size:10px; letter-spacing:0.08em; text-transform:uppercase; text-align:left;
    flex:0 0 auto; white-space:nowrap;
  }
  table.tbl td.cell-name {
    justify-content:flex-start !important; font-size:17px !important; font-weight:700 !important;
    padding:0 0 8px 0 !important; margin-bottom:6px !important;
    border-bottom:1px solid var(--line-soft) !important;
  }
  table.tbl td.cell-name::before { display:none !important; }
  table.tbl td.rank { display:none !important; }
  table.tbl tr.row--q td:first-child, table.tbl tr.row--w td:first-child { box-shadow:none !important; }
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

    df["MeetName"] = m_name
    df["Date"] = m_date_raw
    return df


# Nur diese Spalten werden geladen — schneller und speichersparender als das volle CSV.
_USE_COLS = ["Name", "Sex", "WeightClassKg", "BodyweightKg", "Team", "TotalKg",
             "Place", "Event", "Equipment", "BirthDate", "BirthYear",
             "Best3SquatKg", "Best3BenchKg", "Best3DeadliftKg"]


@st.cache_data(show_spinner="Lade Wettkämpfe …")
def load_data() -> pd.DataFrame:
    """Lädt und verarbeitet alle OeVK-Meets im Qualifikationszeitraum. Ergebnis wird gecacht."""
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

    return pd.concat(all_entries, ignore_index=True) if all_entries else pd.DataFrame()


@st.cache_data(show_spinner="Lade Athlet:innen-Historie …")
def load_full_history() -> pd.DataFrame:
    """Lädt ALLE OeVK-Meets ohne Zeitfenster-Filter. Für Athletenprofile."""
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
    return pd.concat(all_entries, ignore_index=True) if all_entries else pd.DataFrame()


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
        # Sex-Reihenfolge bestimmen: häufigstes Geschlecht
        sex_counts = wc_df["Sex"].astype(str).str.upper().value_counts()
        primary_sex = sex_counts.index[0] if not sex_counts.empty else "M"
        if primary_sex == "F":
            order = [wc_label(w) for w in FEM_ORDER + MAL_ORDER]
        else:
            order = [wc_label(w) for w in MAL_ORDER + FEM_ORDER]
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
            f'<td class="mono">{wc_label(r.WeightClassKg)}</td>'
            f'<td class="num mono">{fmt_kg(r.BodyweightKg, 2)}</td>'
            f'<td class="num mono">{fmt_sbd(getattr(r, "Best3SquatKg", None), getattr(r, "Best3BenchKg", None), getattr(r, "Best3DeadliftKg", None))}</td>'
            f'<td class="num mono-strong">{fmt_kg(r.TotalKg)}</td>'
            f'<td class="num gold-strong">{fmt_kg(getattr(r, "GL_Points", None), 2)}</td>'
            f'<td class="l">{esc(getattr(r, "Team", ""))}</td>'
            '</tr>'
        )
    st.markdown(
        '<div class="tablecard" style="margin-top:14px"><div class="tablescroll"><table class="tbl">'
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
    initial_sidebar_state="expanded",
)
inject_custom_css()

# --- Sidebar-Fold conditional CSS (möglichst FRÜH injizieren, vor jeder sichtbaren Komponente,
# damit der unsichtbare st.markdown-Wrapper keinen Layout-Jump im Hauptbereich verursacht). ---
if st.session_state.get("sb_collapsed", False):
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"], section[data-testid="stSidebar"], aside[data-testid="stSidebar"] {
          min-width:64px !important; width:64px !important; max-width:64px !important;
          overflow:hidden !important;
        }
        [data-testid="stSidebar"] > div:first-child,
        [data-testid="stSidebar"] [data-testid="stSidebarContent"],
        [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
          min-width:64px !important; width:64px !important; max-width:64px !important;
          overflow:hidden !important;
        }
        [data-testid="stSidebar"] [data-testid="stSelectbox"],
        [data-testid="stSidebar"] [data-testid="stCheckbox"],
        [data-testid="stSidebar"] [data-testid="stMarkdown"],
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
        [data-testid="stSidebar"] .sb-divider,
        [data-testid="stSidebar"] .sb-kicker,
        [data-testid="stSidebar"] .sb-scope,
        [data-testid="stSidebar"] .lim-card,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:not(.st-key-sb_toggle_btn) {
          display:none !important; visibility:hidden !important;
        }
        [data-testid="stSidebar"] .st-key-sb_toggle_btn,
        [data-testid="stSidebar"] .st-key-sb_toggle_btn * {
          display:revert !important; visibility:visible !important;
        }
        [data-testid="stSidebar"] .st-key-sb_toggle_btn { display:block !important; }
        .st-key-sb_toggle_btn [data-testid="stButton"] { justify-content:center !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

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
    st.query_params.clear()
    st.rerun()

# Suffix für Widget-Keys — wird beim Reset hochgezählt, damit Widgets als neu gelten.
_GEN = st.session_state.get("_widget_gen", 0)

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
    _back_qs = _filter_qs()
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
          <div class="brand__date">5.–6. September 2026</div>
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

st.markdown(
    '<div class="dev-banner">'
    '<span class="ic">⚠</span>'
    '<span><b>Diese Seite befindet sich in Entwicklung.</b> '
    'Daten und Berechnungen können fehlerhaft sein. '
    'Bitte mit Vorsicht verwenden und im Zweifel auf '
    '<a href="https://www.openpowerlifting.org" target="_blank" '
    'rel="noopener" style="color:var(--gold-bright);text-decoration:none">openpowerlifting.org</a> '
    'gegenprüfen.</span>'
    '</div>',
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

# --- SIDEBAR: Filter ---
# Kombinierte Gewichtsklassen-Optionen (Frauen zuerst, dann Männer).
WC_OPTIONS = [("F", w) for w in FEM_ORDER] + [("M", w) for w in MAL_ORDER]


def _fmt_wc_option(opt) -> str:
    sex, wc = opt
    sex_label = "Frauen" if sex == "F" else "Männer"
    return f"{sex_label} · {wc} kg"


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


# --- Sidebar Fold-Toggle (eigene Steuerung; lässt einen 64px-Streifen sichtbar) ---
if "sb_collapsed" not in st.session_state:
    st.session_state["sb_collapsed"] = False

def _toggle_sb():
    st.session_state["sb_collapsed"] = not st.session_state["sb_collapsed"]

# Conditional fold-CSS wird oben (direkt nach inject_custom_css) injiziert — kein Layout-Jump.
_sb_label = "»" if st.session_state["sb_collapsed"] else "«"
st.sidebar.button(_sb_label, key="sb_toggle_btn", on_click=_toggle_sb)


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

# Filter-Reset-Button — setzt ein Flag und lässt den Top-of-Script-Handler aufräumen,
# bevor die Widgets neu rendern. Vermeidet Probleme mit Streamlits Widget-Cache.
if st.sidebar.button("↺ Filter zurücksetzen", key="reset_filters_btn"):
    st.session_state["_reset_requested"] = True
    st.rerun()

# Checkbox am Ende — getrennt durch Goldlinie
st.sidebar.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
_persist_only_qual = st.session_state.get("_persist_only_qual")
show_only_qualified = st.sidebar.checkbox(
    "Nur Qualifizierte anzeigen",
    value=True if _persist_only_qual is None else bool(_persist_only_qual),
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

# Geschlechterverteilung (alle Athlet:innen im Filterscope) — als Fuß in der Athlet:innen-Karte
_ath_total = max(n_f + n_m, 1)
_ath_pct_f = round(n_f / _ath_total * 100)
_ath_pct_m = 100 - _ath_pct_f if (n_f + n_m) > 0 else 0
athlete_foot = (
    f'<span style="color:var(--gold);font-weight:600">Frauen · {n_f} ({_ath_pct_f}%)</span>'
    f'<span style="opacity:0.4;margin:0 8px">|</span>'
    f'<span style="color:var(--gold);font-weight:600">Männer · {n_m} ({_ath_pct_m}%)</span>'
)

st.markdown(
    '<div class="kpis kpis--3">'
    + kpi_card("Qualifiziert", n_qual, accent=True, foot=qual_foot)
    + kpi_card("Athlet:innen", n_athletes, foot=athlete_foot)
    + kpi_card("Wettkämpfe", n_meets)
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
    def _sh(label: str, sort_type: str = "text", cls: str = "") -> str:
        """Sortierbares Header-Cell — Click wird client-seitig via JS verarbeitet."""
        cls_attr = f' class="{cls} sortable" data-sort-type="{sort_type}"' if cls else f' class="sortable" data-sort-type="{sort_type}"'
        return f'<th{cls_attr}>{label}<span class="sort-arrow">↕</span></th>'

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
    # Client-seitiger Sort — kein Streamlit-Rerun, kein Flash.
    _components.html(
        """
<script>
(function () {
  const doc = window.parent.document;
  function attach() {
    const table = doc.getElementById('qual-table');
    if (!table) return false;
    const ths = table.querySelectorAll('thead tr:last-child th');
    const tbody = table.tBodies[0];
    if (!tbody) return false;
    let state = { col: null, dir: 'desc' };

    function parseNum(s) {
      if (!s) return NaN;
      s = s.replace(/\\s/g, '').replace(/[^\\-+\\d.,]/g, '').replace(',', '.');
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
      if (type === 'num' || type === 'diff') {
        const v = parseNum(text);
        return isNaN(v) ? null : v;
      }
      if (type === 'date') {
        const v = parseDate(text);
        return isNaN(v) ? null : v;
      }
      if (type === 'wc') {
        const plus = text.endsWith('+') ? 0.5 : 0;
        const v = parseNum(text.replace('+', ''));
        return isNaN(v) ? null : v + plus;
      }
      return text.toLowerCase();
    }
    function sortBy(idx, type) {
      const rows = Array.from(tbody.querySelectorAll('tr'));
      const dir = state.dir === 'desc' ? -1 : 1;
      rows.sort(function (a, b) {
        const qa = a.classList.contains('row--q') ? 1 : 0;
        const qb = b.classList.contains('row--q') ? 1 : 0;
        if (qa !== qb) return qb - qa;
        const va = valueOf(a, idx, type);
        const vb = valueOf(b, idx, type);
        if (va === null && vb === null) return 0;
        if (va === null) return 1;
        if (vb === null) return -1;
        if (va < vb) return -1 * dir;
        if (va > vb) return 1 * dir;
        return 0;
      });
      rows.forEach(function (r) { tbody.appendChild(r); });
      // Renumber rank cells (1..N)
      let n = 1;
      tbody.querySelectorAll('tr').forEach(function (r) {
        const rc = r.querySelector('td.rank');
        if (rc) rc.textContent = String(n++);
      });
      ths.forEach(function (h) {
        const a = h.querySelector('.sort-arrow');
        if (a) a.textContent = '↕';
        h.classList.remove('sort-active');
      });
      const active = ths[idx];
      if (active) {
        active.classList.add('sort-active');
        const a = active.querySelector('.sort-arrow');
        if (a) a.textContent = state.dir === 'asc' ? '↑' : '↓';
      }
    }
    ths.forEach(function (th, idx) {
      if (th.classList.contains('nosort')) return;
      th.style.cursor = 'pointer';
      th.addEventListener('click', function () {
        const type = th.dataset.sortType || 'text';
        if (state.col === idx) {
          state.dir = state.dir === 'asc' ? 'desc' : 'asc';
        } else {
          state.col = idx;
          state.dir = (type === 'text') ? 'asc' : 'desc';
        }
        sortBy(idx, type);
      });
    });
    return true;
  }
  // Versuche sofort, dann mit kurzem Retry falls Markdown noch nicht im DOM ist.
  if (!attach()) {
    let tries = 0;
    const id = setInterval(function () {
      if (attach() || ++tries > 30) clearInterval(id);
    }, 100);
  }
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

# --- Credits / Datenquelle ---
st.markdown(
    '<div class="credit">Basiert auf Daten von '
    '<a href="https://www.openpowerlifting.org" target="_blank" rel="noopener">openpowerlifting.org</a> · '
    'OpenIPF-Distribution: <a href="https://www.openipf.org" target="_blank" rel="noopener">openipf.org</a></div>',
    unsafe_allow_html=True,
)
