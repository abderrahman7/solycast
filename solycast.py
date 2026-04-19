import math
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(page_title="SolyCast", layout="wide", page_icon="☀️")

# ── Session state ──
if 'lat' not in st.session_state: st.session_state.lat = 35.704647
if 'lon' not in st.session_state: st.session_state.lon = 0.582941


# ============================================================
# CSS  — uses Streamlit's own CSS variables so it adapts to
# whatever theme (light / dark) the user picks in Settings.
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }

/* Dot-grid atmosphere — colour flips with the theme */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image: radial-gradient(circle, rgba(128,128,128,0.08) 1px, transparent 1px);
    background-size: 32px 32px;
}

/* Warm glow accents that work on both backgrounds */
.stApp::after {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        radial-gradient(ellipse 70% 45% at 12% 8%,  rgba(245,158,11,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 55% at 88% 88%, rgba(59,130,246,0.05)  0%, transparent 60%);
}

.block-container { padding: 2rem 2.5rem 3rem !important; position: relative; z-index: 1; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(245,158,11,0.20) !important;
}
[data-testid="stSidebar"] [data-testid="stSliderTrackFill"] { background: #F59E0B !important; }
[data-testid="stSidebar"] [data-baseweb="slider"] div[role="slider"] {
    background: #F59E0B !important; border-color: #F59E0B !important;
}
[data-testid="stSidebar"] .stNumberInput input { border-radius: 8px !important; }

/* ── Selectbox ── */
[data-baseweb="select"] > div { border-radius: 10px !important; }

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background: rgba(128,128,128,0.07) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(128,128,128,0.12) !important;
    gap: 2px !important;
}
[data-baseweb="tab"] {
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.45rem 1.1rem !important;
    transition: all 0.2s !important;
}
[aria-selected="true"] {
    background: rgba(245,158,11,0.15) !important;
    color: #F59E0B !important;
    border-bottom: none !important;
}
[data-baseweb="tab-highlight"] { display: none !important; }
[data-baseweb="tab-border"]    { display: none !important; }

/* ── Divider ── */
hr { border-color: rgba(128,128,128,0.12) !important; margin: 1.5rem 0 !important; }

/* ── Map container — rounded + shadow ── */
[data-testid="stCustomComponentV1"] {
    border-radius: 18px !important;
    overflow: hidden !important;
    box-shadow: 0 6px 32px rgba(0,0,0,0.18) !important;
    border: 1px solid rgba(245,158,11,0.22) !important;
}
[data-testid="stCustomComponentV1"] iframe { border-radius: 18px !important; display: block; }

/* ── Plotly container ── */
.js-plotly-plot { border-radius: 16px !important; overflow: hidden; }

/* ── Reusable card classes ── */
.sc-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.14);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 16px rgba(0,0,0,0.09);
}
.sc-card-val {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-color);
    line-height: 1.1;
}
.sc-card-unit {
    font-size: 0.82rem;
    font-weight: 400;
    opacity: 0.5;
    margin-left: 3px;
}
.sc-card-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    margin-top: 4px;
    opacity: 0.45;
    color: var(--text-color);
}
.sc-card-icon { font-size: 1.25rem; margin-bottom: 0.25rem; }
.sc-card-glow {
    position: absolute; top: 0; right: 0; width: 64px; height: 64px;
    border-radius: 0 14px 0 0;
}

/* ── Info pill row ── */
.sc-pill-row {
    display: flex; flex-wrap: wrap; gap: 0.55rem; margin-bottom: 1rem;
}
.sc-pill {
    display: flex; align-items: center; gap: 8px;
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.14);
    border-radius: 10px;
    padding: 0.5rem 0.9rem;
    box-shadow: 0 1px 8px rgba(0,0,0,0.07);
}
.sc-pill-icon { font-size: 1.05rem; }
.sc-pill-val {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    line-height: 1.25;
    white-space: normal;
    word-break: break-word;
    max-width: 220px;
}
.sc-pill-lbl {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.45;
    color: var(--text-color);
}

/* ── Daily weather card ── */
.sc-day-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.14);
    border-radius: 12px;
    padding: 0.65rem 0.4rem;
    text-align: center;
    box-shadow: 0 1px 8px rgba(0,0,0,0.07);
}
.sc-day-name {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.45;
    color: var(--text-color);
}
.sc-day-icon  { font-size: 1.6rem; margin: 0.2rem 0; }
.sc-day-temp  { font-size: 0.78rem; font-weight: 500; color: var(--text-color); }
.sc-day-cloud { font-size: 0.65rem; opacity: 0.45; color: var(--text-color); margin-top: 2px; }

/* ── Sidebar section card ── */
.sc-sb-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.12);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.75rem;
}
.sc-sb-section {
    font-family: 'Syne', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    color: #F59E0B;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.65rem;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HTML COMPONENT HELPERS  (no theme dict — use CSS classes)
# ============================================================

def metric_card(label, value, unit="", icon="", accent="#F59E0B", sub=""):
    sub_html = (f'<div style="font-size:0.68rem;opacity:0.45;color:var(--text-color);'
                f'margin-top:3px;line-height:1.3;">{sub}</div>') if sub else ""
    return f"""
    <div class="sc-card">
      <div class="sc-card-glow"
           style="background:radial-gradient(circle at top right,{accent}22,transparent 75%);"></div>
      <div class="sc-card-icon">{icon}</div>
      <div class="sc-card-val">{value}<span class="sc-card-unit">{unit}</span></div>
      <div class="sc-card-label">{label}</div>
      {sub_html}
    </div>"""


def info_pill(items: list):
    """Compact single-line HTML — no blank lines so Markdown never exits HTML-block mode."""
    bits = []
    for item in items:
        icon, label, val, color = item[:4]
        # Build one pill as a single line — no newlines, no blank lines
        bits.append(
            f'<div class="sc-pill">' +
            f'<span class="sc-pill-icon">{icon}</span>' +
            f'<div>' +
            f'<div class="sc-pill-val" style="color:{color};">{val}</div>' +
            f'<div class="sc-pill-lbl">{label}</div>' +
            f'</div></div>'
        )
    return '<div class="sc-pill-row">' + ''.join(bits) + '</div>'


def section_label(text):
    return f"""<div style="font-family:'Syne',sans-serif;font-size:0.72rem;font-weight:700;
                    color:#F59E0B;letter-spacing:0.14em;text-transform:uppercase;
                    margin-bottom:0.5rem;">{text}</div>"""


# ============================================================
# SOLAR PHYSICS ENGINE
# ============================================================

def solar_position(lat, lon, dt_utc):
    doy      = dt_utc.timetuple().tm_yday
    hour_utc = dt_utc.hour + dt_utc.minute / 60.0
    B        = math.radians(360 / 365.0 * (doy - 81))
    decl     = math.radians(23.45 * math.sin(B))
    eot      = 9.87 * math.sin(2*B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
    # Correct UTC → local solar time: no intermediate LST step needed.
    # solar_t (minutes) = UTC_minutes + 4*longitude + EoT
    # This gives the right solar noon for any longitude (e.g. China UTC+8,
    # USA UTC-5/-8) so the clear-sky ceiling aligns with the API forecast.
    solar_t  = hour_utc * 60.0 + 4.0 * lon + eot
    ha       = math.radians((solar_t / 60.0 - 12.0) * 15.0)
    lat_r    = math.radians(lat)
    sin_e    = math.sin(lat_r)*math.sin(decl) + math.cos(lat_r)*math.cos(decl)*math.cos(ha)
    elev     = math.degrees(math.asin(max(-1.0, min(1.0, sin_e))))
    if elev <= 0:
        return 0.0, 180.0
    elev_r   = math.radians(elev)
    cos_az   = ((math.sin(decl) - math.sin(lat_r)*math.sin(elev_r))
                / (math.cos(lat_r)*math.cos(elev_r) + 1e-9))
    az = math.degrees(math.acos(max(-1.0, min(1.0, cos_az))))
    if solar_t > 720: az = 360.0 - az
    return elev, az


def clear_sky_poa(lat, lon, dt_utc, panel_tilt, panel_az):
    """Hottel (1976) clear-sky POA on a tilted surface — no cloud term."""
    elev, sol_az = solar_position(lat, lon, dt_utc)
    if elev <= 0:
        return 0.0
    elev_r   = math.radians(elev)
    sol_az_r = math.radians(sol_az)
    tilt_r   = math.radians(panel_tilt)
    paz_r    = math.radians(panel_az)
    am       = min(38.0, 1.0 / (math.sin(elev_r) + 0.50572*(elev+6.07995)**-1.6364))
    I0       = 1361.0
    DNI      = I0 * (0.129 + 0.756 * math.exp(-0.387 * am))
    DHI      = 0.08 * I0 * math.sin(elev_r)
    cos_aoi  = max(0.0, math.sin(elev_r)*math.cos(tilt_r)
                   + math.cos(elev_r)*math.sin(tilt_r)*math.cos(sol_az_r - paz_r))
    ghi      = DNI * math.sin(elev_r) + DHI
    poa      = DNI*cos_aoi + DHI*(1+math.cos(tilt_r))/2 + ghi*0.2*(1-math.cos(tilt_r))/2
    return max(0.0, poa)


@st.cache_data(ttl=86400)
def compute_annual_yield(lat, lon, tilt, azimuth, capacity):
    lat_abs = abs(lat)
    cf = 0.78 if lat_abs < 20 else 0.82 if lat_abs < 35 else 0.68 if lat_abs < 50 else 0.55
    days    = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    monthly = []
    for m, n in enumerate(days):
        dpoa = sum(clear_sky_poa(lat, lon, datetime(2024, m+1, 15, h, 0), tilt, azimuth)
                   for h in range(24))
        monthly.append(dpoa / 1000.0 * n * capacity * 0.85 * cf)
    return monthly


# ============================================================
# API DATA FETCH — auto-calibrated clear sky ceiling
# ============================================================

@st.cache_data(ttl=300)
def fetch_solycast_data(lat, lon, tilt, azimuth, capacity):
    api_az = azimuth - 180
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
           f"&hourly=global_tilted_irradiance,temperature_2m,cloud_cover,relative_humidity_2m"
           f"&tilt={tilt}&azimuth={api_az}&forecast_days=7")
    try:
        res = requests.get(url, timeout=10).json()
    except Exception as e:
        st.error(f"API request failed: {e}"); return pd.DataFrame()
    if res.get('error') or 'hourly' not in res:
        st.error(f"API error: {res.get('reason','Unknown')}"); return pd.DataFrame()

    times       = pd.to_datetime(res['hourly']['time'])
    physics_poa = [clear_sky_poa(lat, lon, ts.to_pydatetime(), tilt, azimuth) for ts in times]
    actual_gti  = [res['hourly']['global_tilted_irradiance'][i] or 0.0 for i in range(len(times))]

    # Auto-calibrate so clear sky is always genuinely above actual (no clamping equality)
    ratios = [g/p for g, p in zip(actual_gti, physics_poa) if p > 80 and g > 30]
    calib  = max(1.10, min(1.38, max(ratios) * 1.09)) if ratios else 1.14

    actual_kw, clear_kw = [], []
    for i in range(len(times)):
        gti = actual_gti[i]
        hum = res['hourly']['relative_humidity_2m'][i] or 0.0
        hf  = 1.0 - (max(0.0, hum - 50.0) / 50.0) * 0.03
        actual_kw.append((gti / 1000.0) * capacity * 0.85 * hf)
        # Clear sky ceiling capped at 90% of nameplate — accounts for inverter clipping,
        # wiring losses and temperature de-rating on a perfect clear day.
        clear_kw.append(min(0.9 * capacity, (physics_poa[i] / 1000.0) * capacity * 0.85 * calib))

    return pd.DataFrame({
        'Time':         times,
        'Date':         times.date,
        'Predicted_kW': actual_kw,
        'ClearSky_kW':  clear_kw,
        'Temp_C':       [v or 0 for v in res['hourly']['temperature_2m']],
        'Cloud_Pct':    [v or 0 for v in res['hourly']['cloud_cover']],
        'Humidity':     [v or 0 for v in res['hourly']['relative_humidity_2m']],
    })


# ============================================================
# CHART LAYOUT — transparent backgrounds, neutral grids,
# legend always on the right. Works on both Streamlit themes.
# ============================================================

LEGEND_RIGHT = dict(
    orientation="v", x=1.02, y=1, xanchor="left", yanchor="top",
    bgcolor="rgba(0,0,0,0)", borderwidth=0,
    font=dict(family="DM Sans, sans-serif", size=12),
)

def chart_layout(title="", ytitle="", extra=None):
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        font=dict(family="DM Sans, sans-serif", size=12),
        legend=LEGEND_RIGHT,
        xaxis=dict(gridcolor="rgba(128,128,128,0.12)", showline=False,
                   zeroline=False, tickfont=dict(size=11)),
        yaxis=dict(gridcolor="rgba(128,128,128,0.12)", showline=False,
                   zeroline=False, tickfont=dict(size=11),
                   title=dict(text=ytitle) if ytitle else {}),
        margin=dict(l=10, r=150, t=54, b=10),
        title=dict(text=title, font=dict(family="Syne, sans-serif", size=15)),
    )
    if extra:
        base.update(extra)
    return base


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    # Brand
    st.markdown("""
    <div style="text-align:center;padding:1.1rem 0 0.9rem;">
      <div style="display:inline-flex;align-items:center;gap:8px;
                  background:rgba(245,158,11,0.10);border:1px solid rgba(245,158,11,0.28);
                  border-radius:24px;padding:6px 18px;">
        <span style="font-size:1.05rem;">☀️</span>
        <span style="font-family:'Syne',sans-serif;font-size:1.0rem;font-weight:700;
                     color:#F59E0B;">SolyCast</span>
      </div>
      <div style="font-size:0.68rem;opacity:0.4;margin-top:5px;color:var(--text-color);
                  letter-spacing:0.1em;text-transform:uppercase;">Solar Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    # Panel settings card
    st.markdown('<div class="sc-sb-card"><div class="sc-sb-section">⚡ Panel Settings</div>',
                unsafe_allow_html=True)
    capacity = st.number_input("System Capacity (kWp)", value=5.0, step=0.5, min_value=0.5)
    tilt     = st.slider("Tilt (°)", 0, 90, 35)
    azimuth  = st.slider("Orientation — 180° South", 0, 360, 180)
    st.markdown('</div>', unsafe_allow_html=True)

    # Location card
    st.markdown('<div class="sc-sb-card"><div class="sc-sb-section">📍 Location</div>',
                unsafe_allow_html=True)
    lat_m = st.number_input("Latitude",  value=st.session_state.lat, format="%.4f")
    lon_m = st.number_input("Longitude", value=st.session_state.lon, format="%.4f")
    if lat_m != st.session_state.lat or lon_m != st.session_state.lon:
        st.session_state.lat, st.session_state.lon = lat_m, lon_m
    st.markdown(f"""
    <div style="font-size:0.72rem;opacity:0.4;margin-top:0.35rem;
                text-align:center;color:var(--text-color);">
      {st.session_state.lat:.4f}°, {st.session_state.lon:.4f}°
    </div></div>""", unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="margin-top:1.5rem;font-size:0.68rem;opacity:0.35;text-align:center;
                color:var(--text-color);line-height:1.9;">
      <div style="height:1px;background:rgba(245,158,11,0.25);margin-bottom:0.75rem;"></div>
      Data · Open-Meteo API<br>
      Physics · Hottel (1976) clear-sky<br>
      η = 85% STC · Updates hourly
    </div>""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div style="margin-bottom:0.5rem;padding-top:0.2rem;">
  <div style="display:flex;align-items:baseline;gap:14px;">
    <span style="font-family:'Syne',sans-serif;font-size:2.9rem;font-weight:800;
                 background:linear-gradient(135deg,#FBBF24 0%,#F97316 55%,#FB923C 100%);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 background-clip:text;line-height:1.1;">SolyCast</span>
    <span style="font-size:0.8rem;opacity:0.45;color:var(--text-color);
                 letter-spacing:0.12em;text-transform:uppercase;
                 padding:3px 10px;border:1px solid rgba(245,158,11,0.28);
                 border-radius:20px;background:rgba(245,158,11,0.08);">
      Solar Intelligence
    </span>
  </div>
  <p style="font-family:'DM Sans',sans-serif;opacity:0.4;color:var(--text-color);
             font-size:0.9rem;margin:0.2rem 0 0;font-style:italic;">
    Energy output forecast &amp; atmospheric analysis
  </p>
</div>
<div style="height:1px;background:linear-gradient(90deg,rgba(245,158,11,0.5) 0%,
            rgba(59,130,246,0.22) 40%,transparent 100%);margin-bottom:1.4rem;"></div>
""", unsafe_allow_html=True)


# ============================================================
# MAP + METRICS
# ============================================================

col_map, col_metrics = st.columns([1, 2], gap="large")

with col_map:
    st.markdown(section_label("📍 Site Location"), unsafe_allow_html=True)

    m = folium.Map(location=[st.session_state.lat, st.session_state.lon],
                   zoom_start=6,
                   tiles="OpenStreetMap")   # colourful, detailed, theme-agnostic (iframe)
    folium.CircleMarker(
        location=[st.session_state.lat, st.session_state.lon],
        radius=10, color="#F59E0B", fill=True,
        fill_color="#FBBF24", fill_opacity=0.85, weight=2,
    ).add_to(m)
    folium.CircleMarker(
        location=[st.session_state.lat, st.session_state.lon],
        radius=24, color="#F59E0B", fill=False, weight=1, opacity=0.28,
    ).add_to(m)

    map_data = st_folium(m, height=525, width=700, key="main_map")  # 700×525 = 4:3
    if map_data.get("last_clicked"):
        st.session_state.lat = map_data["last_clicked"]["lat"]
        st.session_state.lon = map_data["last_clicked"]["lng"]
        st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:0.4rem;font-size:0.76rem;
                opacity:0.4;color:var(--text-color);">
      Click the map to relocate your site
    </div>""", unsafe_allow_html=True)


# ── Fetch ──
data = fetch_solycast_data(st.session_state.lat, st.session_state.lon, tilt, azimuth, capacity)
if data.empty:
    st.stop()

with col_metrics:
    available_dates = data['Date'].unique()
    st.markdown(section_label("📅 Forecast Day"), unsafe_allow_html=True)
    selected_date = st.selectbox("", available_dates, label_visibility="collapsed")

    is_today     = selected_date == datetime.now().date()
    if is_today:
        metric_label    = "Est. Generation Today"
        metric_sublabel = ""
    else:
        metric_label    = "Est. Generation"
        metric_sublabel = (selected_date.strftime('%A · %d %b')
                           if hasattr(selected_date, 'strftime') else str(selected_date))
    day_df       = data[data['Date'] == selected_date]
    gen_val      = day_df['Predicted_kW'].sum()
    max_val      = day_df['ClearSky_kW'].sum()
    avg_hum      = day_df['Humidity'].mean()
    avg_cld      = day_df['Cloud_Pct'].mean()
    # Temperature Now: row whose UTC hour is closest to the current moment
    from datetime import timezone as _tz
    _now_utc     = datetime.now(_tz.utc).replace(tzinfo=None)
    _now_temp_df = data.copy()
    _now_temp_df['_tdiff'] = (_now_temp_df['Time'] - _now_utc).abs()
    cur_temp     = float(_now_temp_df.loc[_now_temp_df['_tdiff'].idxmin(), 'Temp_C'])
    avg_temp     = cur_temp  # kept as avg_temp so downstream references stay intact
    eff_pct      = (gen_val / max_val * 100) if max_val > 0 else 0

    if   avg_cld < 10: score = 5
    elif avg_cld < 30: score = 4
    elif avg_cld < 50: score = 3
    elif avg_cld < 70: score = 2
    else:              score = 1

    if avg_cld < 20:
        cond_label, cond_color = "Clear Sky", "#FBBF24"
        cond_svg = """<svg width="48" height="48" viewBox="0 0 24 24" fill="none"
          stroke="#FBBF24" stroke-width="1.8" stroke-linecap="round">
          <circle cx="12" cy="12" r="4.5" fill="rgba(251,191,36,0.15)"/>
          <path d="M12 2v2.5M12 19.5V22M4.22 4.22l1.77 1.77M18.01 18.01l1.77 1.77
                   M2 12h2.5M19.5 12H22M4.22 19.78l1.77-1.77M18.01 5.99l1.77-1.77"/>
        </svg>"""
    elif avg_cld < 70:
        cond_label, cond_color = "Partly Cloudy", "#94A3B8"
        cond_svg = """<svg width="48" height="48" viewBox="0 0 24 24" fill="none"
          stroke="#94A3B8" stroke-width="1.8" stroke-linecap="round">
          <circle cx="7" cy="7" r="3" stroke="#FBBF24" fill="rgba(251,191,36,0.12)"/>
          <path d="M7 3v1M7 10v1M3 7h1M10 7h1" stroke="#FBBF24" stroke-width="1.5"/>
          <path d="M17.5 20H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"
                fill="rgba(148,163,184,0.10)"/>
        </svg>"""
    else:
        cond_label, cond_color = "Overcast", "#64748B"
        cond_svg = """<svg width="48" height="48" viewBox="0 0 24 24" fill="none"
          stroke="#64748B" stroke-width="1.8" stroke-linecap="round">
          <path d="M17.5 20H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"
                fill="rgba(100,116,139,0.12)"/>
          <path d="M8 20v2M12 20v2M16 20v2"/>
        </svg>"""

    stars = (f'<span style="color:#FBBF24;font-size:1.35rem;">{"★" * score}</span>'
             f'<span style="color:rgba(128,128,128,0.25);font-size:1.35rem;">{"★" * (5-score)}</span>')

    date_str = (selected_date.strftime('%A, %d %b')
                if hasattr(selected_date, 'strftime') else str(selected_date))

    # Condition banner — uses sc-card class for theme compatibility
    st.markdown(f"""
    <div class="sc-card" style="display:flex;align-items:center;
                justify-content:space-between;padding:1.2rem 1.5rem;margin-bottom:0.9rem;
                border-radius:16px;">
      <div style="display:flex;align-items:center;gap:14px;">
        {cond_svg}
        <div>
          <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:700;
                      color:{cond_color};line-height:1.1;">{cond_label}</div>
          <div style="font-size:0.74rem;opacity:0.45;color:var(--text-color);
                      margin-top:3px;">{date_str}</div>
        </div>
      </div>
      <div style="text-align:right;">
        <div style="margin-bottom:2px;">{stars}</div>
        <div style="font-size:0.66rem;opacity:0.4;color:var(--text-color);
                    letter-spacing:0.1em;text-transform:uppercase;">Solar Score</div>
        <div style="font-size:0.72rem;opacity:0.55;color:var(--text-color);margin-top:3px;">
          {eff_pct:.0f}% of clear-sky potential
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: st.markdown(metric_card(metric_label, f"{gen_val:.2f}", "kWh", "⚡", "#FBBF24", sub=metric_sublabel), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("Clear Sky Ceiling", f"{max_val:.2f}", "kWh", "🌤️", "#60A5FA"), unsafe_allow_html=True)

    st.markdown("<div style='height:0.55rem'></div>", unsafe_allow_html=True)

    c3, c4, c5 = st.columns(3)
    with c3: st.markdown(metric_card("AVG. Cloud Cover",  f"{avg_cld:.0f}",  "%",  "☁️",  "#94A3B8"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("Temperature Now",   f"{avg_temp:.1f}", "°C", "🌡️", "#F87171"), unsafe_allow_html=True)
    with c5: st.markdown(metric_card("AVG. Humidity",     f"{avg_hum:.0f}",  "%",  "💧",  "#60A5FA"), unsafe_allow_html=True)


# ============================================================
# TABS
# ============================================================

st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
st.divider()

t1, t2, t3, t4 = st.tabs([
    "⚡  Production Forecast",
    "⛅  Weather Trends",
    "📅  Annual Yield",
    "📋  Raw Data",
])

# ── Pre-compute week stats ──
week_gen     = data['Predicted_kW'].sum()
daily_totals = data.groupby('Date')['Predicted_kW'].sum()
best_day     = daily_totals.idxmax()
best_day_v   = daily_totals.max()

# Peak: idxmax gives the integer iloc position in the DataFrame
peak_iloc    = data['Predicted_kW'].values.argmax()
peak_kw      = float(data['Predicted_kW'].iloc[peak_iloc])
peak_ts      = data['Time'].iloc[peak_iloc]          # guaranteed pd.Timestamp

week_cs      = data['ClearSky_kW'].sum()
week_eff     = (week_gen / week_cs * 100) if week_cs > 0 else 0
temp_max     = data['Temp_C'].max()
temp_min     = data['Temp_C'].min()
cloud_avg    = data['Cloud_Pct'].mean()
hum_avg      = data['Humidity'].mean()

# Get the first timestamp of the best day — 'Time' column is pd.Timestamp, always safe
best_day_ts  = data.loc[data['Date'] == best_day, 'Time'].iloc[0]
best_day_str = best_day_ts.strftime('%A, %d %b')
peak_day_str = peak_ts.strftime('%a %d %b, %H:%M')

az_dirs  = [(22.5,'N'),(67.5,'NE'),(112.5,'E'),(157.5,'SE'),
            (202.5,'S'),(247.5,'SW'),(292.5,'W'),(337.5,'NW'),(360,'N')]
az_label = next(d for thresh, d in az_dirs if azimuth <= thresh)


# ── Tab 1: Production Forecast ──
with t1:
    st.markdown(info_pill([
        ("🔋", "Capacity",   f"{capacity:.1f} kWp",        "#F59E0B"),
        ("📐", "Tilt",        f"{tilt}°",                    "#F59E0B"),
        ("🧭", "Facing",      az_label,                      "#F59E0B"),
        ("🏆", "Best Day",    f"{best_day_str}  ·  {best_day_v:.1f} kWh",  "#34D399"),
        ("⚡", "Peak Power",  f"{peak_day_str}  ·  {peak_kw:.2f} kW",      "#FBBF24"),
        ("📅", "Week Total",  f"{week_gen:.1f} kWh",         "#60A5FA"),
        ("📊", "Week Eff.",   f"{week_eff:.0f}%",            "#94A3B8"),
    ]), unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['Time'], y=data['ClearSky_kW'],
        name="Clear Sky Ceiling",
        fill='tozeroy', fillcolor='rgba(251,191,36,0.06)',
        line=dict(color='rgba(251,191,36,0.50)', width=1.5, dash='dot'),
        hovertemplate='%{y:.2f} kW<extra>Clear Sky Ceiling</extra>',
    ))
    fig.add_trace(go.Scatter(
        x=data['Time'], y=data['Predicted_kW'],
        name="SolyCast Forecast",
        fill='tozeroy', fillcolor='rgba(59,130,246,0.12)',
        line=dict(color='#60A5FA', width=2.5),
        hovertemplate='%{y:.2f} kW<extra>SolyCast Forecast</extra>',
    ))
    # Shaded "cloud loss" band between ceiling and forecast
    fig.add_trace(go.Scatter(
        x=list(data['Time']) + list(data['Time'])[::-1],
        y=list(data['ClearSky_kW']) + list(data['Predicted_kW'])[::-1],
        fill='toself', fillcolor='rgba(251,191,36,0.04)',
        line=dict(width=0), showlegend=False, hoverinfo='skip',
    ))
    fig.update_layout(**chart_layout("7-Day Energy Output Forecast", "Output (kW)"))
    st.plotly_chart(fig, use_container_width=True)

    # ── Daily summary table ──────────────────────────────────────────────────
    _daily_tbl = data.groupby("Date").agg(
        MinTemp  = ("Temp_C",       "min"),
        MaxTemp  = ("Temp_C",       "max"),
        AvgCloud = ("Cloud_Pct",    "mean"),
        AvgHum   = ("Humidity",     "mean"),
        GenKWh   = ("Predicted_kW", "sum"),
    ).reset_index()

    def _cond(c):
        if c < 20:  return "☀️ Clear"
        if c < 70:  return "⛅ Partly Cloudy"
        return              "☁️ Overcast"

    # Build HTML table rows
    _rows = ""
    for _, r in _daily_tbl.iterrows():
        _date  = r["Date"].strftime("%Y-%m-%d") if hasattr(r["Date"], "strftime") else str(r["Date"])
        _cond_str = _cond(r["AvgCloud"])
        _rows += (
            f'<tr>'
            f'<td>{_date}</td>'
            f'<td>{_cond_str}</td>'
            f'<td>{r["MinTemp"]:.1f}</td>'
            f'<td>{r["MaxTemp"]:.1f}</td>'
            f'<td>{r["AvgCloud"]:.1f}</td>'
            f'<td>{r["AvgHum"]:.1f}</td>'
            f'<td>{r["GenKWh"]:.2f}</td>'
            f'</tr>'
        )

    st.markdown(f"""
    <style>
    .sc-forecast-tbl {{ width:100%; border-collapse:collapse;
        font-family:"DM Sans",sans-serif; font-size:0.875rem; }}
    .sc-forecast-tbl thead tr {{
        background:rgba(245,158,11,0.10);
        border-bottom:1px solid rgba(245,158,11,0.30); }}
    .sc-forecast-tbl th {{
        padding:10px 14px; text-align:left;
        font-family:"Syne",sans-serif; font-size:0.72rem;
        font-weight:700; letter-spacing:0.10em;
        text-transform:uppercase; color:#F59E0B;
        white-space:nowrap; }}
    .sc-forecast-tbl td {{
        padding:11px 14px;
        color:var(--text-color);
        border-bottom:1px solid rgba(128,128,128,0.09); }}
    .sc-forecast-tbl tbody tr:hover {{
        background:rgba(245,158,11,0.05); }}
    .sc-forecast-tbl tbody tr:last-child td {{ border-bottom:none; }}
    </style>
    <div style="background:var(--secondary-background-color);
                border:1px solid rgba(128,128,128,0.14);
                border-radius:14px; overflow:hidden;
                box-shadow:0 2px 16px rgba(0,0,0,0.09);
                margin-top:0.6rem;">
      <table class="sc-forecast-tbl">
        <thead><tr>
          <th>Date</th><th>Condition</th>
          <th>Min °C</th><th>Max °C</th>
          <th>Cloud %</th><th>Humidity %</th>
          <th>Generation (kWh)</th>
        </tr></thead>
        <tbody>{_rows}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)


# ── Tab 2: Weather Trends ──
with t2:
    st.markdown(info_pill([
        ("☀️",  "Best Day",     f"{best_day_str}  ·  {best_day_v:.1f} kWh", "#34D399"),
        ("🌡️", "Temp Range",   f"{temp_min:.0f}–{temp_max:.0f}°C", "#F87171"),
        ("☁️",  "Avg Cloud",    f"{cloud_avg:.0f}%",                 "#94A3B8"),
        ("💧",  "Avg Humidity", f"{hum_avg:.0f}%",                   "#60A5FA"),
    ]), unsafe_allow_html=True)

    # 7 daily weather cards
    daily = data.groupby('Date').agg(
        MaxTemp=('Temp_C','max'), MinTemp=('Temp_C','min'),
        AvgCloud=('Cloud_Pct','mean'),
    ).reset_index()

    dcols = st.columns(len(daily))
    for idx, (_, row) in enumerate(daily.iterrows()):
        cld      = row['AvgCloud']
        day_icon = "☀️" if cld < 20 else ("⛅" if cld < 70 else "☁️")
        day_str  = (row['Date'].strftime('%a') if hasattr(row['Date'], 'strftime')
                    else str(row['Date'])[:3])
        trange   = f"{row['MinTemp']:.0f}–{row['MaxTemp']:.0f}°"
        with dcols[idx]:
            st.markdown(f"""
            <div class="sc-day-card">
              <div class="sc-day-name">{day_str}</div>
              <div class="sc-day-icon">{day_icon}</div>
              <div class="sc-day-temp">{trange}</div>
              <div class="sc-day-cloud">{cld:.0f}% cloud</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    colors_map = {"Temp_C": "#F87171", "Cloud_Pct": "#94A3B8", "Humidity": "#60A5FA"}
    labels_map = {"Temp_C": "Temperature (°C)", "Cloud_Pct": "Cloud Cover (%)", "Humidity": "Humidity (%)"}
    fig_w = go.Figure()
    for col, clr in colors_map.items():
        fig_w.add_trace(go.Scatter(
            x=data['Time'], y=data[col],
            name=labels_map[col],
            line=dict(color=clr, width=2),
            hovertemplate='%{y:.1f}<extra>' + labels_map[col] + '</extra>',
        ))
    fig_w.update_layout(**chart_layout("7-Day Atmospheric Trends"))
    st.plotly_chart(fig_w, use_container_width=True)


# ── Tab 3: Annual Yield ──
with t3:
    monthly_kwh  = compute_annual_yield(st.session_state.lat, st.session_state.lon,
                                        tilt, azimuth, capacity)
    months       = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    total_annual = sum(monthly_kwh)
    peak_month   = months[monthly_kwh.index(max(monthly_kwh))]

    ic1, ic2, ic3 = st.columns(3)
    with ic1: st.markdown(metric_card("Annual Yield",    f"{total_annual:,.0f}", "kWh", "🗓️", "#FBBF24"), unsafe_allow_html=True)
    with ic2: st.markdown(metric_card("Monthly Average", f"{total_annual/12:,.0f}", "kWh", "📊", "#60A5FA"), unsafe_allow_html=True)
    with ic3: st.markdown(metric_card("Peak Month",      peak_month, "", "🏆", "#34D399"), unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    fig_ann = go.Figure(go.Bar(
        x=months, y=monthly_kwh,
        marker=dict(
            color=monthly_kwh,
            colorscale=[[0,'#1E40AF'],[0.55,'#F59E0B'],[1,'#FBBF24']],
            line=dict(width=0),
        ),
        hovertemplate='%{y:,.0f} kWh<extra>%{x}</extra>',
        showlegend=False,
    ))
    fig_ann.update_layout(**chart_layout(
        f"Annual Yield  ·  Tilt {tilt}°  ·  Az {azimuth}° ({az_label})"
        f"  ·  {st.session_state.lat:.1f}°, {st.session_state.lon:.1f}°",
        "Energy (kWh)",
        extra=dict(bargap=0.25, margin=dict(l=10, r=30, t=54, b=10)),
    ))
    st.plotly_chart(fig_ann, use_container_width=True)


# ── Tab 4: Raw Data ──
with t4:
    st.markdown(f"""
    <div style="font-size:0.76rem;opacity:0.4;color:var(--text-color);margin-bottom:0.5rem;">
      Hourly forecast data — all times UTC · {len(data)} rows
    </div>""", unsafe_allow_html=True)
    st.dataframe(
        data.style.format({
            'Predicted_kW': '{:.3f}', 'ClearSky_kW': '{:.3f}',
            'Temp_C': '{:.1f}', 'Cloud_Pct': '{:.0f}', 'Humidity': '{:.0f}',
        }),
        use_container_width=True, height=420,
    )
