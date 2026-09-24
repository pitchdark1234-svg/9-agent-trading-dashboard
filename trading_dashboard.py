"""
Deepcharts-Style Order Flow Terminal (Clone Edition)
+ Simple Username / Password Login

Visual target: Deepcharts dark glassy footprint + volume/delta profile look.
Data: Yahoo Finance OHLC + volume approximation (not real MBO).
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf
import hashlib
import time

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Deepcharts Clone · Order Flow",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ====================== SIMPLE AUTH ======================
# Change these credentials for your own use
USERS = {
    "admin": hashlib.sha256("deepcharts2026".encode()).hexdigest(),
    "trader": hashlib.sha256("orderflow123".encode()).hexdigest(),
}

def check_password(username: str, password: str) -> bool:
    if username not in USERS:
        return False
    return USERS[username] == hashlib.sha256(password.encode()).hexdigest()

def login_page():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
        html, body, .stApp {
            background: #07090d !important;
            font-family: 'JetBrains Mono', monospace !important;
        }
        .login-box {
            max-width: 420px;
            margin: 8vh auto;
            padding: 2.5rem;
            background: rgba(18, 21, 28, 0.75);
            backdrop-filter: blur(18px);
            border: 1px solid rgba(245, 197, 66, 0.25);
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        .login-title {
            color: #f5c542;
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: 3px;
            text-align: center;
            margin-bottom: 0.3rem;
        }
        .login-sub {
            color: #6b7280;
            font-size: 0.75rem;
            text-align: center;
            margin-bottom: 1.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="login-box">
            <div class="login-title">DEEPCHARTS CLONE</div>
            <div class="login-sub">ORDER FLOW · VOLUME PROFILE · DELTA</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin / trader")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("ACCESS TERMINAL", use_container_width=True)

            if submitted:
                if check_password(username.strip(), password):
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = username.strip()
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        st.caption("Default:  admin / deepcharts2026   ·   trader / orderflow123")

# ====================== AUTH GATE ======================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_page()
    st.stop()

# ====================== GLASSY DEEPCHARTS CSS ======================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, .stApp {
    background: #06080c !important;
    font-family: 'Inter', sans-serif !important;
    color: #e8eaed !important;
}
.main .block-container {
    padding: 0.4rem 0.9rem 1rem 0.9rem !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b0e14 0%, #080a0f 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
section[data-testid="stSidebar"] * { font-size: 0.8rem !important; }

h1, h2, h3 {
    color: #f5c542 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
}

div[data-testid="stMetric"] {
    background: rgba(16, 19, 26, 0.7) !important;
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    padding: 9px 12px !important;
}
div[data-testid="stMetric"] label {
    color: #7a808a !important;
    font-size: 0.6rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.9px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #e8eaed !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
}

.stButton > button {
    background: rgba(22, 26, 36, 0.85) !important;
    color: #f5c542 !important;
    border: 1px solid rgba(245, 197, 66, 0.45) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-size: 0.72rem !important;
}
.stButton > button:hover {
    background: #f5c542 !important;
    color: #0c0e12 !important;
}

.dc-header {
    background: linear-gradient(135deg, rgba(18,22,30,0.95) 0%, rgba(10,12,18,0.98) 100%);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.05);
    border-bottom: 2px solid #f5c542;
    border-radius: 12px;
    padding: 11px 16px;
    margin: 0 0 10px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.dc-logo {
    color: #f5c542;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 1.05rem;
    letter-spacing: 2.5px;
    text-shadow: 0 0 18px rgba(245, 197, 66, 0.3);
}
.dc-meta { color: #5a6170; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; }

.dc-ticker {
    background: rgba(16, 19, 26, 0.75);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 9px 14px;
    margin-bottom: 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #9ca3af;
    display: flex;
    flex-wrap: wrap;
    gap: 5px 14px;
    align-items: center;
}

.dc-panel {
    background: rgba(16, 19, 26, 0.6);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 11px 13px;
    margin-bottom: 8px;
}
.dc-panel-title {
    color: #f5c542;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 6px;
    margin-bottom: 9px;
}
.dc-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 3px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
}
.dc-label { color: #7a808a; }
.dc-val { color: #e8eaed; font-weight: 600; }

.poc { color: #ec4899 !important; font-weight: 700; }
.vah { color: #22c55e !important; }
.val { color: #ef4444 !important; }
.hvn { color: #38bdf8 !important; }
.lvn { color: #a78bfa !important; }
.bull { color: #22c55e !important; }
.bear { color: #ef4444 !important; }
.amber { color: #f5c542 !important; }
.delta-pos { color: #22c55e !important; }
.delta-neg { color: #ef4444 !important; }

.fp-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
}
.fp-table th {
    color: #f5c542;
    text-align: left;
    padding: 4px 6px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.fp-table td {
    padding: 3px 6px;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    color: #c5c9d0;
}
.fp-buy { color: #22c55e; }
.fp-sell { color: #ef4444; }

#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stVerticalBlock"] > div { gap: 0.4rem !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ====================== INSTRUMENTS ======================
INSTRUMENTS = {
    "Gold (XAUUSD)": {"yf": "GC=F", "dec": 2},
    "Crude Oil (WTI)": {"yf": "CL=F", "dec": 2},
    "Natural Gas": {"yf": "NG=F", "dec": 3},
    "Bitcoin (BTC)": {"yf": "BTC-USD", "dec": 2},
    "Nifty 50": {"yf": "^NSEI", "dec": 2},
    "Bank Nifty": {"yf": "^NSEBANK", "dec": 2},
}

# ====================== DATA ======================
@st.cache_data(ttl=50)
def fetch_ohlc(symbol, period="5d", interval="15m"):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period=period, interval=interval)
        if df is None or df.empty:
            df = t.history(period="1mo", interval="1h")
        if df is None or df.empty:
            return None
        df = df.reset_index()
        c0 = df.columns[0]
        df = df.rename(columns={
            c0: "time", "Open": "open", "High": "high",
            "Low": "low", "Close": "close", "Volume": "volume"
        })
        df = df[["time", "open", "high", "low", "close", "volume"]].dropna()
        return df.tail(300).reset_index(drop=True)
    except Exception:
        return None

@st.cache_data(ttl=35)
def fetch_last(symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.fast_info
        px = info.get("lastPrice") or info.get("regularMarketPrice")
        prev = info.get("previousClose")
        if px is None:
            h = t.history(period="5d", interval="1d")
            if not h.empty:
                px = float(h["Close"].iloc[-1])
                prev = float(h["Close"].iloc[-2]) if len(h) > 1 else px
        return (float(px) if px else None), (float(prev) if prev else None)
    except Exception:
        return None, None

# ====================== ORDER FLOW ENGINE ======================
def enrich_orderflow(df):
    if df is None or len(df) < 5:
        return None
    d = df.copy().reset_index(drop=True)
    d["range"] = (d["high"] - d["low"]).replace(0, np.nan)
    d["body"] = (d["close"] - d["open"]).abs()
    d["buy_vol"] = d["volume"] * ((d["close"] - d["low"]) / d["range"]).fillna(0.5)
    d["sell_vol"] = d["volume"] * ((d["high"] - d["close"]) / d["range"]).fillna(0.5)
    d["delta"] = d["buy_vol"] - d["sell_vol"]
    d["cvd"] = d["delta"].cumsum()
    d["body_pct"] = (d["body"] / d["range"]).fillna(0)
    d["upper_wick"] = d["high"] - d[["open", "close"]].max(axis=1)
    d["lower_wick"] = d[["open", "close"]].min(axis=1) - d["low"]
    return d

def build_volume_profile(df, bins=72, va_pct=0.70):
    if df is None or len(df) < 10 or df["volume"].sum() <= 0:
        return None
    price_min = float(df["low"].min())
    price_max = float(df["high"].max())
    if price_max <= price_min:
        return None

    edges = np.linspace(price_min, price_max, bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    vol = np.zeros(bins)
    buy_vol = np.zeros(bins)
    sell_vol = np.zeros(bins)

    for _, row in df.iterrows():
        lo, hi = float(row["low"]), float(row["high"])
        v = float(row["volume"])
        bv = float(row.get("buy_vol", v * 0.5))
        sv = float(row.get("sell_vol", v * 0.5))
        if hi <= lo:
            idx = int(np.clip(np.searchsorted(edges, (lo + hi) / 2, side="right") - 1, 0, bins - 1))
            vol[idx] += v
            buy_vol[idx] += bv
            sell_vol[idx] += sv
            continue
        i0 = int(np.clip(np.searchsorted(edges, lo, side="right") - 1, 0, bins - 1))
        i1 = int(np.clip(np.searchsorted(edges, hi, side="right") - 1, 0, bins - 1))
        n = max(1, i1 - i0 + 1)
        for i in range(i0, i1 + 1):
            vol[i] += v / n
            buy_vol[i] += bv / n
            sell_vol[i] += sv / n

    total = vol.sum()
    if total <= 0:
        return None

    poc_idx = int(np.argmax(vol))
    poc = float(centers[poc_idx])
    target = total * va_pct
    left = right = poc_idx
    covered = vol[poc_idx]
    while covered < target and (left > 0 or right < bins - 1):
        lv = vol[left - 1] if left > 0 else -1
        rv = vol[right + 1] if right < bins - 1 else -1
        if rv >= lv and right < bins - 1:
            right += 1
            covered += vol[right]
        elif left > 0:
            left -= 1
            covered += vol[left]
        else:
            right += 1
            covered += vol[right]

    return {
        "centers": centers, "edges": edges, "volume": vol,
        "buy_vol": buy_vol, "sell_vol": sell_vol,
        "delta": buy_vol - sell_vol,
        "poc": poc, "poc_idx": poc_idx,
        "vah": float(edges[right + 1]), "val": float(edges[left]),
        "total": total, "price_min": price_min, "price_max": price_max,
    }

def detect_hvn_lvn(profile, sensitivity=0.55):
    if profile is None:
        return [], []
    vol = profile["volume"]
    centers = profile["centers"]
    if vol.max() <= 0:
        return [], []
    mean_v, std_v = vol.mean(), vol.std() + 1e-12
    thr_h = mean_v + sensitivity * std_v
    thr_l = mean_v - sensitivity * std_v * 0.45
    hvn, lvn = [], []
    for i in range(1, len(vol) - 1):
        if vol[i] >= vol[i-1] and vol[i] >= vol[i+1] and vol[i] >= thr_h:
            hvn.append({"price": float(centers[i]), "volume": float(vol[i]),
                        "pct": float(vol[i] / profile["total"] * 100)})
        if vol[i] <= vol[i-1] and vol[i] <= vol[i+1] and vol[i] <= max(thr_l, 0):
            lvn.append({"price": float(centers[i]), "volume": float(vol[i]),
                        "pct": float(vol[i] / profile["total"] * 100)})
    hvn = sorted(hvn, key=lambda x: x["volume"], reverse=True)[:8]
    lvn = sorted(lvn, key=lambda x: x["volume"])[:6]
    return hvn, lvn

def detect_absorption(df, min_vol_mult=1.8, max_body_pct=0.35):
    if df is None or len(df) < 20:
        return []
    d = df.copy()
    avg_vol = d["volume"].rolling(20, min_periods=5).mean()
    events = []
    for i in range(len(d)):
        row = d.loc[i]
        av = avg_vol.iloc[i] if not pd.isna(avg_vol.iloc[i]) else row["volume"]
        if av <= 0 or row.get("range", 0) is None or (
            isinstance(row.get("range"), float) and (pd.isna(row["range"]) or row["range"] <= 0)
        ):
            continue
        if row["volume"] < av * min_vol_mult:
            continue
        bp = row.get("body_pct", 1)
        if pd.isna(bp) or bp > max_body_pct:
            continue
        uw, lw = row.get("upper_wick", 0), row.get("lower_wick", 0)
        body = row.get("body", 0)
        if lw > body * 1.2 and row["close"] >= row["open"]:
            events.append({
                "type": "ASK ABSORPTION", "side": "BUY",
                "price": float(row["low"]), "volume": float(row["volume"]),
                "delta": float(row.get("delta", 0)), "time": row["time"],
                "note": "Buyers absorbed sell pressure"
            })
        elif uw > body * 1.2 and row["close"] <= row["open"]:
            events.append({
                "type": "BID ABSORPTION", "side": "SELL",
                "price": float(row["high"]), "volume": float(row["volume"]),
                "delta": float(row.get("delta", 0)), "time": row["time"],
                "note": "Sellers absorbed buy pressure"
            })
    return events[-15:]

def compute_vwap(df):
    if df is None or len(df) < 2:
        return None
    tp = (df["high"] + df["low"] + df["close"]) / 3
    cum_v = df["volume"].cumsum().replace(0, np.nan)
    vwap = (tp * df["volume"]).cumsum() / cum_v
    return float(vwap.iloc[-1]) if not pd.isna(vwap.iloc[-1]) else None

def heat_color(intensity, positive=True):
    intensity = float(np.clip(intensity, 0, 1))
    if positive:
        r = int(6 + (34 - 6) * intensity)
        g = int(30 + (197 - 30) * intensity)
        b = int(30 + (94 - 30) * intensity)
    else:
        r = int(30 + (239 - 30) * intensity)
        g = int(15 + (68 - 15) * intensity)
        b = int(15 + (68 - 15) * intensity)
    return f"rgb({r},{g},{b})"

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("### DEEPCHARTS CLONE")
    st.caption(f"Logged in as **{st.session_state.get('user', '—')}**")
    if st.button("LOGOUT", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("user", None)
        st.rerun()

    st.markdown("---")
    if st.button("REFRESH DATA", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    auto = st.toggle("Auto refresh", value=False)
    rate = st.slider("Seconds", 20, 120, 45)

    st.markdown("---")
    st.markdown("### MARKET")
    selected = st.selectbox("Instrument", list(INSTRUMENTS.keys()), index=0)
    inst = INSTRUMENTS[selected]
    yf_sym, dec = inst["yf"], inst["dec"]

    st.markdown("---")
    st.markdown("### PROFILE")
    lookback = st.slider("Lookback bars", 40, 280, 140, 10)
    n_bins = st.slider("Profile bins", 40, 100, 72, 4)
    va_pct = st.slider("Value Area %", 50, 90, 70, 5) / 100.0
    hvn_sens = st.slider("HVN/LVN sensitivity", 0.25, 1.4, 0.55, 0.05)

    st.markdown("---")
    st.markdown("### DISPLAY")
    show_candles = st.toggle("Candles", value=True)
    show_fp_overlay = st.toggle("Footprint delta markers", value=True)
    show_vp = st.toggle("Volume Profile", value=True)
    show_delta_profile = st.toggle("Delta Profile", value=True)
    show_heat = st.toggle("Heat intensity", value=True)
    show_poc = st.toggle("POC", value=True)
    show_va = st.toggle("Value Area", value=True)
    show_hvn = st.toggle("HVN", value=True)
    show_lvn = st.toggle("LVN", value=True)
    show_vwap = st.toggle("VWAP", value=True)
    show_cvd = st.toggle("CVD panel", value=True)
    show_abs = st.toggle("Absorption", value=True)

    st.markdown("---")
    st.markdown("### ABSORPTION")
    abs_mult = st.slider("Min vol × avg", 1.3, 3.0, 1.8, 0.1)
    abs_body = st.slider("Max body/range", 0.15, 0.50, 0.35, 0.05)

    st.markdown("---")
    chart_h = st.slider("Chart height px", 560, 980, 780, 20)

    st.markdown("---")
    st.caption("Approx. order-flow from OHLC volume.")
    st.caption("True Deepcharts needs tick/MBO data.")

# ====================== LOAD & COMPUTE ======================
raw = fetch_ohlc(yf_sym)
if raw is not None:
    ohlc = enrich_orderflow(raw.tail(lookback).reset_index(drop=True))
else:
    ohlc = None

last_px, prev_px = fetch_last(yf_sym)
if last_px is None and ohlc is not None and len(ohlc):
    last_px = float(ohlc["close"].iloc[-1])
    prev_px = float(ohlc["close"].iloc[-2]) if len(ohlc) > 1 else last_px
if last_px is None:
    last_px, prev_px = 0.0, 0.0

dpx = last_px - (prev_px or last_px)
dpct = (dpx / last_px * 100) if last_px else 0

profile = build_volume_profile(ohlc, bins=n_bins, va_pct=va_pct)
hvn_list, lvn_list = detect_hvn_lvn(profile, sensitivity=hvn_sens) if profile else ([], [])
absorptions = detect_absorption(ohlc, min_vol_mult=abs_mult, max_body_pct=abs_body) if (show_abs and ohlc is not None) else []
vwap_val = compute_vwap(ohlc) if show_vwap else None

session_delta = float(ohlc["delta"].sum()) if ohlc is not None else 0
session_cvd = float(ohlc["cvd"].iloc[-1]) if ohlc is not None else 0
buy_tot = float(ohlc["buy_vol"].sum()) if ohlc is not None else 0
sell_tot = float(ohlc["sell_vol"].sum()) if ohlc is not None else 0

# ====================== HEADER ======================
now = datetime.now()
st.markdown(f"""
<div class="dc-header">
  <div>
    <span class="dc-logo">DEEPCHARTS CLONE</span>
    <span style="color:#2a3142;margin:0 10px;">│</span>
    <span style="color:#e8eaed;font-size:0.9rem;font-family:'JetBrains Mono',monospace;">{selected}</span>
    <span style="color:#2a3142;margin:0 10px;">│</span>
    <span style="color:#5a6170;font-size:0.68rem;font-family:'JetBrains Mono',monospace;">
      FOOTPRINT · DELTA PROFILE · HEAT · CVD · HVN · ABSORPTION
    </span>
  </div>
  <div class="dc-meta">{now.strftime('%Y-%m-%d %H:%M:%S')} IST · {st.session_state.get('user','')}</div>
</div>
""", unsafe_allow_html=True)

poc_s = f"{profile['poc']:.{dec}f}" if profile else "—"
vah_s = f"{profile['vah']:.{dec}f}" if profile else "—"
val_s = f"{profile['val']:.{dec}f}" if profile else "—"
dcls = "bull" if dpx >= 0 else "bear"
sdcls = "delta-pos" if session_delta >= 0 else "delta-neg"

st.markdown(f"""
<div class="dc-ticker">
  <span style="color:#f5c542;font-weight:700;">{yf_sym}</span>
  <span style="color:#fff;font-weight:700;font-size:1.1rem;">{last_px:,.{dec}f}</span>
  <span class="{dcls}">{dpx:+.{dec}f} ({dpct:+.2f}%)</span>
  <span style="color:#2a3142;">│</span>
  <span>POC <span class="poc">{poc_s}</span></span>
  <span>VAH <span class="vah">{vah_s}</span></span>
  <span>VAL <span class="val">{val_s}</span></span>
  <span style="color:#2a3142;">│</span>
  <span>Δ <span class="{sdcls}">{session_delta:+,.0f}</span></span>
  <span>CVD <span class="{sdcls}">{session_cvd:+,.0f}</span></span>
  <span style="color:#2a3142;">│</span>
  <span>HVN <span class="hvn">{len(hvn_list)}</span></span>
  <span>LVN <span class="lvn">{len(lvn_list)}</span></span>
  <span>ABS <span class="amber">{len(absorptions)}</span></span>
  {"<span>VWAP <span class='amber'>" + f"{vwap_val:.{dec}f}" + "</span></span>" if vwap_val else ""}
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
c1.metric("LAST", f"{last_px:,.{dec}f}", f"{dpx:+.{dec}f}")
c2.metric("POC", poc_s)
c3.metric("VAH / VAL", f"{vah_s} / {val_s}")
c4.metric("SESSION Δ", f"{session_delta:+,.0f}")
c5.metric("CVD", f"{session_cvd:+,.0f}")
c6.metric("BUY / SELL", f"{buy_tot:,.0f} / {sell_tot:,.0f}")
c7.metric("ABSORPTION", len(absorptions))

# ====================== MAIN CHART ======================
main_col, side_col = st.columns([2.5, 1])

with main_col:
    st.markdown('<div class="dc-panel-title">ORDER FLOW CHART — VOLUME / DELTA / HEAT PROFILE</div>', unsafe_allow_html=True)

    if ohlc is None or len(ohlc) < 5:
        st.warning("No data. Click REFRESH or change instrument.")
    else:
        rows = 2 if show_cvd else 1
        row_heights = [0.73, 0.27] if show_cvd else [1.0]
        fig = make_subplots(
            rows=rows, cols=2,
            column_widths=[0.75, 0.25],
            row_heights=row_heights,
            shared_xaxes=True,
            horizontal_spacing=0.01,
            vertical_spacing=0.03,
            specs=[[{"secondary_y": False}, {"secondary_y": False}]] +
                  ([[{"colspan": 2}, None]] if show_cvd else []),
        )

        if show_candles:
            fig.add_trace(go.Candlestick(
                x=ohlc["time"], open=ohlc["open"], high=ohlc["high"],
                low=ohlc["low"], close=ohlc["close"], name="OHLC",
                increasing_line_color="#22c55e", decreasing_line_color="#ef4444",
                increasing_fillcolor="rgba(34,197,94,0.82)",
                decreasing_fillcolor="rgba(239,68,68,0.82)",
                whiskerwidth=0.5, line=dict(width=1),
            ), row=1, col=1)

        if show_fp_overlay:
            max_abs_d = ohlc["delta"].abs().max() + 1e-9
            sizes = 4 + 15 * (ohlc["delta"].abs() / max_abs_d)
            colors = ["rgba(34,197,94,0.4)" if d >= 0 else "rgba(239,68,68,0.4)" for d in ohlc["delta"]]
            fig.add_trace(go.Scatter(
                x=ohlc["time"], y=ohlc["close"], mode="markers",
                marker=dict(size=sizes, color=colors, symbol="circle", line=dict(width=0)),
                name="Bar Δ", hovertemplate="Δ %{customdata:,.0f}<extra></extra>",
                customdata=ohlc["delta"],
            ), row=1, col=1)

        if show_vwap and vwap_val:
            fig.add_hline(y=vwap_val, line_dash="dot", line_color="rgba(245,197,66,0.9)",
                          line_width=1.4, annotation_text=f"VWAP {vwap_val:.{dec}f}",
                          annotation_position="top right",
                          annotation_font=dict(size=10, color="#f5c542"), row=1, col=1)

        if profile:
            if show_poc:
                fig.add_hline(y=profile["poc"], line_color="#ec4899", line_width=2.1,
                              annotation_text=f"POC {profile['poc']:.{dec}f}",
                              annotation_position="bottom left",
                              annotation_font=dict(size=10, color="#ec4899"), row=1, col=1)
            if show_va:
                fig.add_hrect(y0=profile["val"], y1=profile["vah"],
                              fillcolor="rgba(34,197,94,0.05)", line_width=0, row=1, col=1)
                fig.add_hline(y=profile["vah"], line_dash="dash", line_color="rgba(34,197,94,0.8)",
                              line_width=1.2, annotation_text="VAH",
                              annotation_font=dict(size=9, color="#22c55e"), row=1, col=1)
                fig.add_hline(y=profile["val"], line_dash="dash", line_color="rgba(239,68,68,0.8)",
                              line_width=1.2, annotation_text="VAL",
                              annotation_font=dict(size=9, color="#ef4444"), row=1, col=1)

            if show_hvn:
                for h in hvn_list[:5]:
                    fig.add_hline(y=h["price"], line_color="rgba(56,189,248,0.5)",
                                  line_width=1, line_dash="dot", row=1, col=1)
            if show_lvn:
                for lv in lvn_list[:4]:
                    fig.add_hline(y=lv["price"], line_color="rgba(167,139,250,0.4)",
                                  line_width=1, line_dash="dot", row=1, col=1)

            if show_vp or show_delta_profile:
                max_v = profile["volume"].max() + 1e-9
                bar_x = profile["delta"] if show_delta_profile else profile["volume"]
                bar_colors = []
                for i in range(len(profile["volume"])):
                    if i == profile["poc_idx"]:
                        bar_colors.append("#ec4899")
                        continue
                    if show_heat:
                        intens = profile["volume"][i] / max_v
                        pos = profile["delta"][i] >= 0
                        bar_colors.append(heat_color(intens, positive=pos))
                    elif show_delta_profile:
                        bar_colors.append("#22c55e" if profile["delta"][i] >= 0 else "#ef4444")
                    else:
                        bar_colors.append("rgba(56,189,248,0.85)")

                fig.add_trace(go.Bar(
                    x=bar_x, y=profile["centers"], orientation="h",
                    marker=dict(color=bar_colors, line=dict(width=0), opacity=0.88),
                    name="Delta Profile" if show_delta_profile else "Volume Profile",
                    hovertemplate=("Price %{y:." + str(dec) + "f}<br>Vol %{customdata[0]:.0f}<br>"
                                   "Δ %{customdata[1]:+.0f}<extra></extra>"),
                    customdata=np.column_stack([profile["volume"], profile["delta"]]),
                ), row=1, col=2)

        if show_abs and absorptions:
            fig.add_trace(go.Scatter(
                x=[a["time"] for a in absorptions],
                y=[a["price"] for a in absorptions],
                mode="markers",
                marker=dict(size=12, symbol="diamond",
                            color=["#22c55e" if a["side"] == "BUY" else "#ef4444" for a in absorptions],
                            line=dict(width=1.3, color="rgba(255,255,255,0.7)"), opacity=0.9),
                name="Absorption", text=[a["type"] for a in absorptions],
                hovertemplate="%{text}<br>%{y:." + str(dec) + "f}<extra></extra>",
            ), row=1, col=1)

        if show_cvd:
            fig.add_trace(go.Scatter(
                x=ohlc["time"], y=ohlc["cvd"], mode="lines",
                line=dict(color="#f5c542", width=1.5),
                fill="tozeroy", fillcolor="rgba(245,197,66,0.06)",
                name="CVD", hovertemplate="CVD %{y:+,.0f}<extra></extra>",
            ), row=2, col=1)
            fig.add_hline(y=0, line_color="rgba(40,46,60,0.8)", line_width=1, row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            height=chart_h,
            margin=dict(l=6, r=6, t=14, b=6),
            paper_bgcolor="rgba(6,8,12,0)",
            plot_bgcolor="rgba(10,12,18,0.7)",
            font=dict(family="JetBrains Mono, monospace", color="#7a808a", size=10),
            xaxis_rangeslider_visible=False,
            showlegend=False,
            hovermode="x unified",
            bargap=0.03,
        )
        fig.update_xaxes(showgrid=False, color="#3d4452", zeroline=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(22,26,36,0.8)", color="#7a808a",
                         zeroline=False, row=1, col=1)
        fig.update_yaxes(showgrid=False, color="#7a808a", zeroline=False, row=1, col=2)
        if show_cvd:
            fig.update_yaxes(showgrid=True, gridcolor="rgba(22,26,36,0.8)",
                             title_text="CVD", row=2, col=1)

        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with side_col:
    st.markdown('<div class="dc-panel-title">KEY LEVELS</div>', unsafe_allow_html=True)
    if profile:
        st.markdown(f"""
        <div class="dc-panel">
          <div class="dc-row"><span class="dc-label">POC</span><span class="poc">{profile['poc']:.{dec}f}</span></div>
          <div class="dc-row"><span class="dc-label">VAH</span><span class="vah">{profile['vah']:.{dec}f}</span></div>
          <div class="dc-row"><span class="dc-label">VAL</span><span class="val">{profile['val']:.{dec}f}</span></div>
          <div class="dc-row"><span class="dc-label">VWAP</span><span class="amber">{f"{vwap_val:.{dec}f}" if vwap_val else "—"}</span></div>
          <div class="dc-row"><span class="dc-label">VA %</span><span class="dc-val">{int(va_pct*100)}%</span></div>
          <div class="dc-row"><span class="dc-label">Bins</span><span class="dc-val">{n_bins}</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="dc-panel-title">ORDER FLOW SUMMARY</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dc-panel">
      <div class="dc-row"><span class="dc-label">Buy volume</span><span class="bull">{buy_tot:,.0f}</span></div>
      <div class="dc-row"><span class="dc-label">Sell volume</span><span class="bear">{sell_tot:,.0f}</span></div>
      <div class="dc-row"><span class="dc-label">Session Δ</span><span class="{sdcls}">{session_delta:+,.0f}</span></div>
      <div class="dc-row"><span class="dc-label">CVD</span><span class="{sdcls}">{session_cvd:+,.0f}</span></div>
      <div class="dc-row"><span class="dc-label">Bias</span><span class="{sdcls}">{"BUYERS" if session_delta > 0 else "SELLERS" if session_delta < 0 else "FLAT"}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="dc-panel-title">HVN</div>', unsafe_allow_html=True)
    if hvn_list:
        for h in hvn_list[:5]:
            st.markdown(f"""
            <div class="dc-panel" style="border-left:3px solid #38bdf8;padding:7px 9px;margin-bottom:5px;">
              <div class="dc-row"><span class="hvn">HVN</span><span class="dc-val">{h['price']:.{dec}f}</span></div>
              <div class="dc-row"><span class="dc-label">Share</span><span class="dc-label">{h['pct']:.1f}%</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No HVN")

    st.markdown('<div class="dc-panel-title">LVN</div>', unsafe_allow_html=True)
    if lvn_list:
        for lv in lvn_list[:4]:
            st.markdown(f"""
            <div class="dc-panel" style="border-left:3px solid #a78bfa;padding:7px 9px;margin-bottom:5px;">
              <div class="dc-row"><span class="lvn">LVN</span><span class="dc-val">{lv['price']:.{dec}f}</span></div>
              <div class="dc-row"><span class="dc-label">Share</span><span class="dc-label">{lv['pct']:.1f}%</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No LVN")

    st.markdown('<div class="dc-panel-title">ABSORPTION</div>', unsafe_allow_html=True)
    if absorptions:
        for a in reversed(absorptions[-5:]):
            col = "#22c55e" if a["side"] == "BUY" else "#ef4444"
            st.markdown(f"""
            <div class="dc-panel" style="border-left:3px solid {col};padding:7px 9px;margin-bottom:5px;">
              <div class="dc-row"><span style="color:{col};font-weight:700;">{a['type']}</span>
              <span class="dc-val">{a['price']:.{dec}f}</span></div>
              <div style="color:#5a6170;font-size:0.68rem;">{a['note']} · Δ {a['delta']:+.0f}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No absorption")

# ====================== FOOTPRINT TABLE ======================
st.markdown("---")
st.markdown('<div class="dc-panel-title">FOOTPRINT-STYLE TAPE (RECENT BARS)</div>', unsafe_allow_html=True)
st.caption("Approximate buy/sell volume per bar — not true tick footprint")

if ohlc is not None and len(ohlc) > 0:
    tail = ohlc.tail(16).iloc[::-1]
    rows_html = ""
    for _, r in tail.iterrows():
        dlt = r["delta"]
        dcls = "fp-buy" if dlt >= 0 else "fp-sell"
        tstr = r["time"].strftime("%m-%d %H:%M") if hasattr(r["time"], "strftime") else str(r["time"])[:16]
        rows_html += f"""
        <tr>
          <td>{tstr}</td>
          <td>{r['open']:.{dec}f}</td>
          <td>{r['high']:.{dec}f}</td>
          <td>{r['low']:.{dec}f}</td>
          <td>{r['close']:.{dec}f}</td>
          <td class="fp-buy">{r['buy_vol']:,.0f}</td>
          <td class="fp-sell">{r['sell_vol']:,.0f}</td>
          <td class="{dcls}">{dlt:+,.0f}</td>
          <td>{r['volume']:,.0f}</td>
        </tr>"""
    st.markdown(f"""
    <div class="dc-panel" style="overflow-x:auto;">
      <table class="fp-table">
        <thead>
          <tr>
            <th>TIME</th><th>O</th><th>H</th><th>L</th><th>C</th>
            <th>BUY VOL</th><th>SELL VOL</th><th>DELTA</th><th>TOTAL</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)

st.caption(
    f"Deepcharts Clone · {yf_sym} · POC {poc_s} · Δ {session_delta:+,.0f} · "
    f"CVD {session_cvd:+,.0f} · Approx. from OHLC · User: {st.session_state.get('user','')}"
)

if auto:
    time.sleep(rate)
    st.rerun()
