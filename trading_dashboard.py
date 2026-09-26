"""
Deepcharts-Style Order Flow Terminal (TradingView Layout Edition)
- Large chart first (full width)
- Timeframes: 1m · 5m · 15m · 1h · 4h · 1D · 1W · 1M
- Multi EMA with settings
- ICT concepts (FVG, Order Blocks, Liquidity, Structure)
- Volume / Delta Profile · CVD · Absorption
- Login security

Data: Yahoo Finance (approximation — not real MBO)
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf
import time

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Deepcharts Clone · Order Flow",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ====================== AUTH ======================
VALID_USERS = {
    "admin": "deepcharts2026",
    "trader": "orderflow123",
}

def login_page():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
        html, body, .stApp { background: #07090d !important; font-family: 'JetBrains Mono', monospace !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="text-align:center; margin-top:8vh; margin-bottom:1.5rem;">
            <div style="color:#f5c542; font-size:1.5rem; font-weight:700; letter-spacing:3px;">DEEPCHARTS CLONE</div>
            <div style="color:#6b7280; font-size:0.8rem; margin-top:6px;">ORDER FLOW · ICT · EMA · VOLUME PROFILE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([1, 1.3, 1])
    with c2:
        username = st.text_input("Username", key="login_user", placeholder="admin")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="deepcharts2026")
        if st.button("ACCESS TERMINAL", type="primary", use_container_width=True):
            u = username.strip().lower()
            p = password.strip()
            if u in VALID_USERS and VALID_USERS[u] == p:
                st.session_state["authenticated"] = True
                st.session_state["user"] = u
                st.rerun()
            else:
                st.error("Invalid credentials. Use: admin / deepcharts2026")
        st.info("**admin** / deepcharts2026   ·   **trader** / orderflow123")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    login_page()
    st.stop()

# ====================== CSS ======================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
html, body, .stApp { background: #06080c !important; font-family: 'Inter', sans-serif !important; color: #e8eaed !important; }
.main .block-container { padding: 0.35rem 0.8rem 1rem 0.8rem !important; max-width: 100% !important; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b0e14 0%, #080a0f 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
section[data-testid="stSidebar"] * { font-size: 0.78rem !important; }
div[data-testid="stMetric"] {
    background: rgba(16,19,26,0.7) !important; backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 8px !important; padding: 8px 10px !important;
}
div[data-testid="stMetric"] label {
    color: #7a808a !important; font-size: 0.58rem !important; text-transform: uppercase !important;
    letter-spacing: 0.8px !important; font-family: 'JetBrains Mono', monospace !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #e8eaed !important; font-family: 'JetBrains Mono', monospace !important; font-size: 1.05rem !important;
}
.stButton > button {
    background: rgba(22,26,36,0.85) !important; color: #f5c542 !important;
    border: 1px solid rgba(245,197,66,0.4) !important; border-radius: 7px !important;
    font-family: 'JetBrains Mono', monospace !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.8px !important; font-size: 0.7rem !important;
}
.stButton > button:hover { background: #f5c542 !important; color: #0c0e12 !important; }
.dc-header {
    background: linear-gradient(135deg, rgba(18,22,30,0.95) 0%, rgba(10,12,18,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.05); border-bottom: 2px solid #f5c542;
    border-radius: 10px; padding: 10px 14px; margin: 0 0 8px 0;
    display: flex; justify-content: space-between; align-items: center;
}
.dc-logo { color: #f5c542; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1rem; letter-spacing: 2px; }
.dc-meta { color: #5a6170; font-size: 0.68rem; font-family: 'JetBrains Mono', monospace; }
.dc-ticker {
    background: rgba(16,19,26,0.75); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; color: #9ca3af;
    display: flex; flex-wrap: wrap; gap: 5px 12px; align-items: center;
}
.dc-panel {
    background: rgba(16,19,26,0.6); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;
}
.dc-panel-title {
    color: #f5c542; font-family: 'JetBrains Mono', monospace; font-size: 0.64rem;
    font-weight: 700; letter-spacing: 1.4px; text-transform: uppercase;
    border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 5px; margin-bottom: 8px;
}
.dc-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 3px 0; border-bottom: 1px solid rgba(255,255,255,0.03);
    font-family: 'JetBrains Mono', monospace; font-size: 0.74rem;
}
.dc-label { color: #7a808a; } .dc-val { color: #e8eaed; font-weight: 600; }
.poc { color: #ec4899 !important; font-weight: 700; }
.vah { color: #22c55e !important; } .val { color: #ef4444 !important; }
.hvn { color: #38bdf8 !important; } .lvn { color: #a78bfa !important; }
.bull { color: #22c55e !important; } .bear { color: #ef4444 !important; }
.amber { color: #f5c542 !important; }
.delta-pos { color: #22c55e !important; } .delta-neg { color: #ef4444 !important; }
.fp-table { width: 100%; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; }
.fp-table th { color: #f5c542; text-align: left; padding: 4px 5px; border-bottom: 1px solid rgba(255,255,255,0.08); }
.fp-table td { padding: 3px 5px; border-bottom: 1px solid rgba(255,255,255,0.03); color: #c5c9d0; }
.fp-buy { color: #22c55e; } .fp-sell { color: #ef4444; }
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stVerticalBlock"] > div { gap: 0.35rem !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ====================== INSTRUMENTS & TIMEFRAMES ======================
INSTRUMENTS = {
    "Gold (XAUUSD)": {"yf": "GC=F", "dec": 2},
    "Crude Oil (WTI)": {"yf": "CL=F", "dec": 2},
    "Natural Gas": {"yf": "NG=F", "dec": 3},
    "Bitcoin (BTC)": {"yf": "BTC-USD", "dec": 2},
    "Nifty 50": {"yf": "^NSEI", "dec": 2},
    "Bank Nifty": {"yf": "^NSEBANK", "dec": 2},
}

TF_MAP = {
    "1m":  {"interval": "1m",  "period": "7d",   "resample": None},
    "5m":  {"interval": "5m",  "period": "60d",  "resample": None},
    "15m": {"interval": "15m", "period": "60d",  "resample": None},
    "1h":  {"interval": "1h",  "period": "730d", "resample": None},
    "4h":  {"interval": "1h",  "period": "730d", "resample": "4h"},
    "1D":  {"interval": "1d",  "period": "5y",   "resample": None},
    "1W":  {"interval": "1wk", "period": "10y",  "resample": None},
    "1M":  {"interval": "1mo", "period": "max",  "resample": None},
}

# ====================== DATA ======================
@st.cache_data(ttl=45)
def fetch_ohlc(symbol, timeframe="15m", lookback_bars=200):
    cfg = TF_MAP.get(timeframe, TF_MAP["15m"])
    try:
        t = yf.Ticker(symbol)
        df = t.history(period=cfg["period"], interval=cfg["interval"])
        if df is None or df.empty:
            df = t.history(period="1y", interval="1d")
        if df is None or df.empty:
            return None
        df = df.reset_index()
        c0 = df.columns[0]
        df = df.rename(columns={
            c0: "time", "Open": "open", "High": "high",
            "Low": "low", "Close": "close", "Volume": "volume"
        })
        df = df[["time", "open", "high", "low", "close", "volume"]].dropna()
        if cfg["resample"] == "4h":
            df = df.set_index("time")
            o = df["open"].resample("4h").first()
            h = df["high"].resample("4h").max()
            l = df["low"].resample("4h").min()
            c = df["close"].resample("4h").last()
            v = df["volume"].resample("4h").sum()
            df = pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "volume": v}).dropna().reset_index()
            df = df.rename(columns={"index": "time"})
        return df.tail(lookback_bars).reset_index(drop=True)
    except Exception:
        return None

@st.cache_data(ttl=30)
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

# ====================== ORDER FLOW ======================
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

def build_volume_profile(df, bins=64, va_pct=0.70):
    if df is None or len(df) < 10 or df["volume"].sum() <= 0:
        return None
    price_min, price_max = float(df["low"].min()), float(df["high"].max())
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
            vol[idx] += v; buy_vol[idx] += bv; sell_vol[idx] += sv
            continue
        i0 = int(np.clip(np.searchsorted(edges, lo, side="right") - 1, 0, bins - 1))
        i1 = int(np.clip(np.searchsorted(edges, hi, side="right") - 1, 0, bins - 1))
        n = max(1, i1 - i0 + 1)
        for i in range(i0, i1 + 1):
            vol[i] += v / n; buy_vol[i] += bv / n; sell_vol[i] += sv / n
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
            right += 1; covered += vol[right]
        elif left > 0:
            left -= 1; covered += vol[left]
        else:
            right += 1; covered += vol[right]
    return {
        "centers": centers, "edges": edges, "volume": vol,
        "buy_vol": buy_vol, "sell_vol": sell_vol, "delta": buy_vol - sell_vol,
        "poc": poc, "poc_idx": poc_idx,
        "vah": float(edges[right + 1]), "val": float(edges[left]),
        "total": total, "price_min": price_min, "price_max": price_max,
    }

def detect_hvn_lvn(profile, sensitivity=0.55):
    if profile is None:
        return [], []
    vol, centers = profile["volume"], profile["centers"]
    if vol.max() <= 0:
        return [], []
    mean_v, std_v = vol.mean(), vol.std() + 1e-12
    thr_h = mean_v + sensitivity * std_v
    thr_l = mean_v - sensitivity * std_v * 0.45
    hvn, lvn = [], []
    for i in range(1, len(vol) - 1):
        if vol[i] >= vol[i-1] and vol[i] >= vol[i+1] and vol[i] >= thr_h:
            hvn.append({"price": float(centers[i]), "volume": float(vol[i]), "pct": float(vol[i]/profile["total"]*100)})
        if vol[i] <= vol[i-1] and vol[i] <= vol[i+1] and vol[i] <= max(thr_l, 0):
            lvn.append({"price": float(centers[i]), "volume": float(vol[i]), "pct": float(vol[i]/profile["total"]*100)})
    return sorted(hvn, key=lambda x: x["volume"], reverse=True)[:8], sorted(lvn, key=lambda x: x["volume"])[:6]

def detect_absorption(df, min_vol_mult=1.8, max_body_pct=0.35):
    if df is None or len(df) < 20:
        return []
    d = df.copy()
    avg_vol = d["volume"].rolling(20, min_periods=5).mean()
    events = []
    for i in range(len(d)):
        row = d.loc[i]
        av = avg_vol.iloc[i] if not pd.isna(avg_vol.iloc[i]) else row["volume"]
        if av <= 0 or pd.isna(row.get("range", 0)) or row.get("range", 0) <= 0:
            continue
        if row["volume"] < av * min_vol_mult:
            continue
        bp = row.get("body_pct", 1)
        if pd.isna(bp) or bp > max_body_pct:
            continue
        uw, lw, body = row.get("upper_wick", 0), row.get("lower_wick", 0), row.get("body", 0)
        if lw > body * 1.2 and row["close"] >= row["open"]:
            events.append({"type": "ASK ABSORPTION", "side": "BUY", "price": float(row["low"]),
                           "volume": float(row["volume"]), "delta": float(row.get("delta", 0)),
                           "time": row["time"], "note": "Buyers absorbed sell pressure"})
        elif uw > body * 1.2 and row["close"] <= row["open"]:
            events.append({"type": "BID ABSORPTION", "side": "SELL", "price": float(row["high"]),
                           "volume": float(row["volume"]), "delta": float(row.get("delta", 0)),
                           "time": row["time"], "note": "Sellers absorbed buy pressure"})
    return events[-12:]

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
        r = int(6 + (34-6)*intensity); g = int(30+(197-30)*intensity); b = int(30+(94-30)*intensity)
    else:
        r = int(30+(239-30)*intensity); g = int(15+(68-15)*intensity); b = int(15+(68-15)*intensity)
    return f"rgb({r},{g},{b})"

# ====================== ICT ======================
def detect_fvg(df, min_gap_pct=0.05):
    if df is None or len(df) < 5:
        return []
    fvgs = []
    for i in range(2, len(df)):
        c0, c1, c2 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]
        if c2["low"] > c0["high"]:
            gap = c2["low"] - c0["high"]
            mid = (c0["high"] + c2["low"]) / 2
            if gap / mid * 100 >= min_gap_pct:
                fvgs.append({"type": "BULL FVG", "side": "BUY", "top": float(c2["low"]),
                             "bottom": float(c0["high"]), "mid": float(mid), "time": c2["time"]})
        if c2["high"] < c0["low"]:
            gap = c0["low"] - c2["high"]
            mid = (c2["high"] + c0["low"]) / 2
            if gap / mid * 100 >= min_gap_pct:
                fvgs.append({"type": "BEAR FVG", "side": "SELL", "top": float(c0["low"]),
                             "bottom": float(c2["high"]), "mid": float(mid), "time": c2["time"]})
    return fvgs[-20:]

def detect_order_blocks(df, lookback=50, body_ratio=0.55):
    if df is None or len(df) < 30:
        return []
    obs = []
    d = df.tail(lookback).reset_index(drop=True)
    for i in range(3, len(d) - 2):
        row = d.iloc[i]
        body = abs(row["close"] - row["open"])
        rng = row["high"] - row["low"]
        if rng <= 0 or body / rng < body_ratio:
            continue
        if row["close"] < row["open"]:
            future_high = d.iloc[i+1:i+4]["high"].max() if i+4 <= len(d) else row["high"]
            if future_high > row["high"] * 1.001:
                obs.append({"type": "BULL OB", "side": "BUY", "top": float(row["high"]),
                            "bottom": float(row["low"]), "time": row["time"], "price": float(row["close"])})
        if row["close"] > row["open"]:
            future_low = d.iloc[i+1:i+4]["low"].min() if i+4 <= len(d) else row["low"]
            if future_low < row["low"] * 0.999:
                obs.append({"type": "BEAR OB", "side": "SELL", "top": float(row["high"]),
                            "bottom": float(row["low"]), "time": row["time"], "price": float(row["close"])})
    return obs[-12:]

def detect_liquidity(df):
    if df is None or len(df) < 20:
        return [], []
    highs, lows = [], []
    d = df.tail(80).reset_index(drop=True)
    for i in range(2, len(d) - 2):
        if (d.iloc[i]["high"] > d.iloc[i-1]["high"] and d.iloc[i]["high"] > d.iloc[i-2]["high"] and
            d.iloc[i]["high"] > d.iloc[i+1]["high"] and d.iloc[i]["high"] > d.iloc[i+2]["high"]):
            highs.append({"price": float(d.iloc[i]["high"]), "time": d.iloc[i]["time"]})
        if (d.iloc[i]["low"] < d.iloc[i-1]["low"] and d.iloc[i]["low"] < d.iloc[i-2]["low"] and
            d.iloc[i]["low"] < d.iloc[i+1]["low"] and d.iloc[i]["low"] < d.iloc[i+2]["low"]):
            lows.append({"price": float(d.iloc[i]["low"]), "time": d.iloc[i]["time"]})
    return highs[-6:], lows[-6:]

def detect_structure(df):
    if df is None or len(df) < 30:
        return "—", None
    d = df.tail(40)
    recent_high = d["high"].iloc[-10:].max()
    recent_low = d["low"].iloc[-10:].min()
    prev_high = d["high"].iloc[-25:-10].max()
    prev_low = d["low"].iloc[-25:-10].min()
    last = float(d["close"].iloc[-1])
    if last > prev_high and recent_high > prev_high:
        return "BULLISH BOS", last
    if last < prev_low and recent_low < prev_low:
        return "BEARISH BOS", last
    if last > prev_high:
        return "BULLISH CHoCH?", last
    if last < prev_low:
        return "BEARISH CHoCH?", last
    return "RANGE / BALANCE", last

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("### DEEPCHARTS CLONE")
    st.caption(f"User: **{st.session_state.get('user', '—')}**")
    if st.button("LOGOUT", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("user", None)
        st.rerun()
    st.markdown("---")
    if st.button("REFRESH", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    auto = st.toggle("Auto refresh", value=False)
    rate = st.slider("Seconds", 20, 120, 50)

    st.markdown("---")
    st.markdown("### MARKET")
    selected = st.selectbox("Instrument", list(INSTRUMENTS.keys()), index=0)
    inst = INSTRUMENTS[selected]
    yf_sym, dec = inst["yf"], inst["dec"]

    st.markdown("---")
    st.markdown("### TIMEFRAME")
    timeframe = st.selectbox("TF", list(TF_MAP.keys()), index=2)
    lookback = st.slider("Bars", 50, 400, 180, 10)

    st.markdown("---")
    st.markdown("### EMA SETTINGS")
    show_ema = st.toggle("Show EMAs", value=True)
    ema_periods = st.multiselect(
        "EMA Periods",
        options=[5, 8, 9, 13, 21, 34, 50, 55, 89, 100, 144, 200, 233],
        default=[9, 21, 50, 200],
    )
    ema_colors = {
        5: "#f472b6", 8: "#fb923c", 9: "#fbbf24", 13: "#a3e635",
        21: "#34d399", 34: "#22d3ee", 50: "#60a5fa", 55: "#818cf8",
        89: "#a78bfa", 100: "#c084fc", 144: "#e879f9", 200: "#f472b6", 233: "#fb7185",
    }

    st.markdown("---")
    st.markdown("### ICT CONCEPTS")
    show_fvg = st.toggle("Fair Value Gaps", value=True)
    show_ob = st.toggle("Order Blocks", value=True)
    show_liq = st.toggle("Liquidity (Swing H/L)", value=True)
    show_structure = st.toggle("Market Structure", value=True)
    fvg_min = st.slider("FVG min gap %", 0.02, 0.5, 0.08, 0.02)

    st.markdown("---")
    st.markdown("### PROFILE / FLOW")
    n_bins = st.slider("Profile bins", 40, 100, 64, 4)
    va_pct = st.slider("Value Area %", 50, 90, 70, 5) / 100.0
    hvn_sens = st.slider("HVN sensitivity", 0.25, 1.4, 0.55, 0.05)
    show_vp = st.toggle("Volume Profile", value=True)
    show_delta_profile = st.toggle("Delta Profile", value=True)
    show_heat = st.toggle("Heat", value=True)
    show_poc = st.toggle("POC", value=True)
    show_va = st.toggle("Value Area", value=True)
    show_hvn = st.toggle("HVN", value=True)
    show_lvn = st.toggle("LVN", value=True)
    show_vwap = st.toggle("VWAP", value=True)
    show_cvd = st.toggle("CVD panel", value=True)
    show_abs = st.toggle("Absorption", value=True)
    abs_mult = st.slider("Abs vol x", 1.3, 3.0, 1.8, 0.1)

    st.markdown("---")
    chart_h = st.slider("Chart height", 600, 1100, 820, 20)
    st.caption("Yahoo OHLC approximation - not real MBO")

# ====================== LOAD DATA ======================
raw = fetch_ohlc(yf_sym, timeframe=timeframe, lookback_bars=lookback)
ohlc = enrich_orderflow(raw) if raw is not None else None

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
absorptions = detect_absorption(ohlc, min_vol_mult=abs_mult) if (show_abs and ohlc is not None) else []
vwap_val = compute_vwap(ohlc) if show_vwap else None

fvgs = detect_fvg(ohlc, min_gap_pct=fvg_min) if (show_fvg and ohlc is not None) else []
obs = detect_order_blocks(ohlc) if (show_ob and ohlc is not None) else []
liq_highs, liq_lows = detect_liquidity(ohlc) if (show_liq and ohlc is not None) else ([], [])
structure_label, structure_px = detect_structure(ohlc) if (show_structure and ohlc is not None) else ("—", None)

session_delta = float(ohlc["delta"].sum()) if ohlc is not None else 0
session_cvd = float(ohlc["cvd"].iloc[-1]) if ohlc is not None else 0
buy_tot = float(ohlc["buy_vol"].sum()) if ohlc is not None else 0
sell_tot = float(ohlc["sell_vol"].sum()) if ohlc is not None else 0

ema_data = {}
if show_ema and ohlc is not None and ema_periods:
    for p in ema_periods:
        if len(ohlc) >= p:
            ema_data[p] = ohlc["close"].ewm(span=p, adjust=False).mean()

# ====================== HEADER ======================
now = datetime.now()
st.markdown(f"""
<div class="dc-header">
  <div>
    <span class="dc-logo">DEEPCHARTS CLONE</span>
    <span style="color:#2a3142;margin:0 8px;">|</span>
    <span style="color:#e8eaed;font-size:0.88rem;font-family:'JetBrains Mono',monospace;">{selected}</span>
    <span style="color:#2a3142;margin:0 8px;">|</span>
    <span style="color:#f5c542;font-size:0.85rem;font-family:'JetBrains Mono',monospace;font-weight:600;">{timeframe}</span>
    <span style="color:#2a3142;margin:0 8px;">|</span>
    <span style="color:#5a6170;font-size:0.66rem;font-family:'JetBrains Mono',monospace;">ICT · EMA · PROFILE · CVD</span>
  </div>
  <div class="dc-meta">{now.strftime('%Y-%m-%d %H:%M')} IST · {st.session_state.get('user','')}</div>
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
  <span style="color:#fff;font-weight:700;font-size:1.08rem;">{last_px:,.{dec}f}</span>
  <span class="{dcls}">{dpx:+.{dec}f} ({dpct:+.2f}%)</span>
  <span style="color:#2a3142;">|</span>
  <span>TF <span class="amber">{timeframe}</span></span>
  <span>POC <span class="poc">{poc_s}</span></span>
  <span>VAH <span class="vah">{vah_s}</span></span>
  <span>VAL <span class="val">{val_s}</span></span>
  <span style="color:#2a3142;">|</span>
  <span>Δ <span class="{sdcls}">{session_delta:+,.0f}</span></span>
  <span>CVD <span class="{sdcls}">{session_cvd:+,.0f}</span></span>
  <span style="color:#2a3142;">|</span>
  <span>Structure <span class="amber">{structure_label}</span></span>
</div>
""", unsafe_allow_html=True)

# ====================== BIG CHART ======================
st.markdown('<div class="dc-panel-title">CHART — CANDLES · EMA · ICT · VOLUME / DELTA PROFILE</div>', unsafe_allow_html=True)

if ohlc is None or len(ohlc) < 5:
    st.warning("No data for this timeframe / symbol. Try another TF or click REFRESH.")
else:
    rows = 2 if show_cvd else 1
    row_heights = [0.78, 0.22] if show_cvd else [1.0]
    use_profile = (show_vp or show_delta_profile) and profile is not None
    cols = 2 if use_profile else 1
    col_widths = [0.78, 0.22] if use_profile else [1.0]

    if use_profile:
        specs = [[{"secondary_y": False}, {"secondary_y": False}]]
        if show_cvd:
            specs.append([{"colspan": 2}, None])
        fig = make_subplots(rows=rows, cols=2, column_widths=col_widths, row_heights=row_heights,
                            shared_xaxes=True, horizontal_spacing=0.008, vertical_spacing=0.025, specs=specs)
    else:
        specs = [[{"secondary_y": False}]]
        if show_cvd:
            specs.append([{"secondary_y": False}])
        fig = make_subplots(rows=rows, cols=1, row_heights=row_heights,
                            shared_xaxes=True, vertical_spacing=0.025, specs=specs)

    fig.add_trace(go.Candlestick(
        x=ohlc["time"], open=ohlc["open"], high=ohlc["high"],
        low=ohlc["low"], close=ohlc["close"], name="OHLC",
        increasing_line_color="#26a69a", decreasing_line_color="#ef5350",
        increasing_fillcolor="#26a69a", decreasing_fillcolor="#ef5350",
        whiskerwidth=0.4, line=dict(width=1),
    ), row=1, col=1)

    if show_ema and ema_data:
        for p, series in ema_data.items():
            color = ema_colors.get(p, "#94a3b8")
            fig.add_trace(go.Scatter(
                x=ohlc["time"], y=series, mode="lines",
                line=dict(color=color, width=1.4), name=f"EMA {p}",
                hovertemplate=f"EMA {p}: %{{y:.{dec}f}}<extra></extra>",
            ), row=1, col=1)

    if show_vwap and vwap_val:
        fig.add_hline(y=vwap_val, line_dash="dot", line_color="rgba(245,197,66,0.9)",
                      line_width=1.3, annotation_text=f"VWAP {vwap_val:.{dec}f}",
                      annotation_font=dict(size=10, color="#f5c542"), row=1, col=1)

    if show_fvg and fvgs:
        for f in fvgs[-10:]:
            color = "rgba(34,197,94,0.15)" if f["side"] == "BUY" else "rgba(239,68,68,0.15)"
            fig.add_hrect(y0=f["bottom"], y1=f["top"], fillcolor=color, line_width=0, row=1, col=1, layer="below")

    if show_ob and obs:
        for o in obs[-6:]:
            color = "rgba(56,189,248,0.12)" if o["side"] == "BUY" else "rgba(167,139,250,0.12)"
            fig.add_hrect(y0=o["bottom"], y1=o["top"], fillcolor=color, line_width=0, row=1, col=1, layer="below")

    if show_liq:
        for h in liq_highs[-4:]:
            fig.add_hline(y=h["price"], line_color="rgba(239,68,68,0.45)", line_width=1, line_dash="dot", row=1, col=1)
        for l in liq_lows[-4:]:
            fig.add_hline(y=l["price"], line_color="rgba(34,197,94,0.45)", line_width=1, line_dash="dot", row=1, col=1)

    if profile:
        if show_poc:
            fig.add_hline(y=profile["poc"], line_color="#ec4899", line_width=2,
                          annotation_text=f"POC {profile['poc']:.{dec}f}",
                          annotation_font=dict(size=10, color="#ec4899"), row=1, col=1)
        if show_va:
            fig.add_hrect(y0=profile["val"], y1=profile["vah"], fillcolor="rgba(34,197,94,0.04)", line_width=0, row=1, col=1)
            fig.add_hline(y=profile["vah"], line_dash="dash", line_color="rgba(34,197,94,0.75)", line_width=1.1, row=1, col=1)
            fig.add_hline(y=profile["val"], line_dash="dash", line_color="rgba(239,68,68,0.75)", line_width=1.1, row=1, col=1)
        if show_hvn:
            for h in hvn_list[:4]:
                fig.add_hline(y=h["price"], line_color="rgba(56,189,248,0.45)", line_width=1, line_dash="dot", row=1, col=1)
        if show_lvn:
            for lv in lvn_list[:3]:
                fig.add_hline(y=lv["price"], line_color="rgba(167,139,250,0.4)", line_width=1, line_dash="dot", row=1, col=1)

    if show_abs and absorptions:
        fig.add_trace(go.Scatter(
            x=[a["time"] for a in absorptions], y=[a["price"] for a in absorptions],
            mode="markers",
            marker=dict(size=11, symbol="diamond",
                        color=["#22c55e" if a["side"] == "BUY" else "#ef4444" for a in absorptions],
                        line=dict(width=1.2, color="rgba(255,255,255,0.6)")),
            name="Absorption", text=[a["type"] for a in absorptions],
            hovertemplate="%{text}<br>%{y:." + str(dec) + "f}<extra></extra>",
        ), row=1, col=1)

    if use_profile:
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
            marker=dict(color=bar_colors, line=dict(width=0), opacity=0.88), name="Profile",
            hovertemplate=("Price %{y:." + str(dec) + "f}<br>Vol %{customdata[0]:.0f}<br>Δ %{customdata[1]:+.0f}<extra></extra>"),
            customdata=np.column_stack([profile["volume"], profile["delta"]]),
        ), row=1, col=2)

    if show_cvd:
        fig.add_trace(go.Scatter(
            x=ohlc["time"], y=ohlc["cvd"], mode="lines",
            line=dict(color="#f5c542", width=1.4),
            fill="tozeroy", fillcolor="rgba(245,197,66,0.06)", name="CVD",
            hovertemplate="CVD %{y:+,.0f}<extra></extra>",
        ), row=2, col=1)
        fig.add_hline(y=0, line_color="rgba(40,46,60,0.8)", line_width=1, row=2, col=1)

    fig.update_layout(
        template="plotly_dark", height=chart_h,
        margin=dict(l=4, r=4, t=8, b=4),
        paper_bgcolor="rgba(6,8,12,0)", plot_bgcolor="rgba(10,12,18,0.85)",
        font=dict(family="JetBrains Mono, monospace", color="#7a808a", size=10),
        xaxis_rangeslider_visible=False, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified", bargap=0.03, dragmode="pan",
    )
    fig.update_xaxes(showgrid=False, color="#3d4452", zeroline=False, rangeslider_visible=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(22,26,36,0.75)", color="#7a808a", zeroline=False, row=1, col=1)
    if use_profile:
        fig.update_yaxes(showgrid=False, color="#7a808a", zeroline=False, row=1, col=2)
    if show_cvd:
        fig.update_yaxes(showgrid=True, gridcolor="rgba(22,26,36,0.75)", title_text="CVD", row=2, col=1)

    st.plotly_chart(fig, width="stretch", config={
        "displayModeBar": True, "scrollZoom": True,
        "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
    })

# ====================== METRICS BELOW ======================
m1, m2, m3, m4, m5, m6, m7, m8 = st.columns(8)
m1.metric("LAST", f"{last_px:,.{dec}f}", f"{dpx:+.{dec}f}")
m2.metric("POC", poc_s)
m3.metric("VAH", vah_s)
m4.metric("VAL", val_s)
m5.metric("SESSION Δ", f"{session_delta:+,.0f}")
m6.metric("CVD", f"{session_cvd:+,.0f}")
m7.metric("STRUCTURE", structure_label[:12] if structure_label else "—")
m8.metric("FVG / OB", f"{len(fvgs)} / {len(obs)}")

# ====================== DETAILS BELOW ======================
st.markdown("---")
col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.markdown('<div class="dc-panel-title">KEY LEVELS</div>', unsafe_allow_html=True)
    if profile:
        st.markdown(f"""
        <div class="dc-panel">
          <div class="dc-row"><span class="dc-label">POC</span><span class="poc">{profile['poc']:.{dec}f}</span></div>
          <div class="dc-row"><span class="dc-label">VAH</span><span class="vah">{profile['vah']:.{dec}f}</span></div>
          <div class="dc-row"><span class="dc-label">VAL</span><span class="val">{profile['val']:.{dec}f}</span></div>
          <div class="dc-row"><span class="dc-label">VWAP</span><span class="amber">{f"{vwap_val:.{dec}f}" if vwap_val else "—"}</span></div>
          <div class="dc-row"><span class="dc-label">VA %</span><span class="dc-val">{int(va_pct*100)}%</span></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="dc-panel-title">ORDER FLOW</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dc-panel">
      <div class="dc-row"><span class="dc-label">Buy vol</span><span class="bull">{buy_tot:,.0f}</span></div>
      <div class="dc-row"><span class="dc-label">Sell vol</span><span class="bear">{sell_tot:,.0f}</span></div>
      <div class="dc-row"><span class="dc-label">Session Δ</span><span class="{sdcls}">{session_delta:+,.0f}</span></div>
      <div class="dc-row"><span class="dc-label">Bias</span><span class="{sdcls}">{"BUYERS" if session_delta > 0 else "SELLERS" if session_delta < 0 else "FLAT"}</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown('<div class="dc-panel-title">ICT — STRUCTURE</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dc-panel">
      <div class="dc-row"><span class="dc-label">Structure</span><span class="amber">{structure_label}</span></div>
      <div class="dc-row"><span class="dc-label">FVGs</span><span class="dc-val">{len(fvgs)}</span></div>
      <div class="dc-row"><span class="dc-label">Order Blocks</span><span class="dc-val">{len(obs)}</span></div>
      <div class="dc-row"><span class="dc-label">Liq Highs</span><span class="bear">{len(liq_highs)}</span></div>
      <div class="dc-row"><span class="dc-label">Liq Lows</span><span class="bull">{len(liq_lows)}</span></div>
    </div>
    """, unsafe_allow_html=True)
    if fvgs:
        st.markdown('<div class="dc-panel-title">RECENT FVG</div>', unsafe_allow_html=True)
        for f in reversed(fvgs[-4:]):
            col = "#22c55e" if f["side"] == "BUY" else "#ef4444"
            st.markdown(f"""
            <div class="dc-panel" style="border-left:3px solid {col};padding:6px 8px;margin-bottom:4px;">
              <div class="dc-row"><span style="color:{col};font-weight:700;">{f['type']}</span>
              <span class="dc-val">{f['mid']:.{dec}f}</span></div>
              <div style="color:#5a6170;font-size:0.65rem;">{f['bottom']:.{dec}f} → {f['top']:.{dec}f}</div>
            </div>
            """, unsafe_allow_html=True)

with col_c:
    st.markdown('<div class="dc-panel-title">ORDER BLOCKS</div>', unsafe_allow_html=True)
    if obs:
        for o in reversed(obs[-5:]):
            col = "#38bdf8" if o["side"] == "BUY" else "#a78bfa"
            st.markdown(f"""
            <div class="dc-panel" style="border-left:3px solid {col};padding:6px 8px;margin-bottom:4px;">
              <div class="dc-row"><span style="color:{col};font-weight:700;">{o['type']}</span>
              <span class="dc-val">{o['price']:.{dec}f}</span></div>
              <div style="color:#5a6170;font-size:0.65rem;">{o['bottom']:.{dec}f} – {o['top']:.{dec}f}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No OB detected")
    st.markdown('<div class="dc-panel-title">LIQUIDITY</div>', unsafe_allow_html=True)
    if liq_highs or liq_lows:
        for h in liq_highs[-3:]:
            st.markdown(f"""
            <div class="dc-panel" style="border-left:3px solid #ef4444;padding:5px 8px;margin-bottom:3px;">
              <div class="dc-row"><span class="bear">SELL LIQ</span><span class="dc-val">{h['price']:.{dec}f}</span></div>
            </div>
            """, unsafe_allow_html=True)
        for l in liq_lows[-3:]:
            st.markdown(f"""
            <div class="dc-panel" style="border-left:3px solid #22c55e;padding:5px 8px;margin-bottom:3px;">
              <div class="dc-row"><span class="bull">BUY LIQ</span><span class="dc-val">{l['price']:.{dec}f}</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No swing liquidity")

with col_d:
    st.markdown('<div class="dc-panel-title">HVN / LVN</div>', unsafe_allow_html=True)
    if hvn_list:
        for h in hvn_list[:4]:
            st.markdown(f"""
            <div class="dc-panel" style="border-left:3px solid #38bdf8;padding:5px 8px;margin-bottom:3px;">
              <div class="dc-row"><span class="hvn">HVN</span><span class="dc-val">{h['price']:.{dec}f}</span></div>
              <div class="dc-row"><span class="dc-label">Share</span><span class="dc-label">{h['pct']:.1f}%</span></div>
            </div>
            """, unsafe_allow_html=True)
    if lvn_list:
        for lv in lvn_list[:3]:
            st.markdown(f"""
            <div class="dc-panel" style="border-left:3px solid #a78bfa;padding:5px 8px;margin-bottom:3px;">
              <div class="dc-row"><span class="lvn">LVN</span><span class="dc-val">{lv['price']:.{dec}f}</span></div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('<div class="dc-panel-title">ABSORPTION</div>', unsafe_allow_html=True)
    if absorptions:
        for a in reversed(absorptions[-4:]):
            col = "#22c55e" if a["side"] == "BUY" else "#ef4444"
            st.markdown(f"""
            <div class="dc-panel" style="border-left:3px solid {col};padding:5px 8px;margin-bottom:3px;">
              <div class="dc-row"><span style="color:{col};font-weight:700;font-size:0.7rem;">{a['type']}</span>
              <span class="dc-val">{a['price']:.{dec}f}</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No absorption")

# ====================== FOOTPRINT ======================
st.markdown("---")
st.markdown('<div class="dc-panel-title">FOOTPRINT TAPE (RECENT BARS)</div>', unsafe_allow_html=True)
if ohlc is not None and len(ohlc) > 0:
    tail = ohlc.tail(14).iloc[::-1]
    rows_html = ""
    for _, r in tail.iterrows():
        dlt = r["delta"]
        dcls = "fp-buy" if dlt >= 0 else "fp-sell"
        tstr = r["time"].strftime("%m-%d %H:%M") if hasattr(r["time"], "strftime") else str(r["time"])[:16]
        rows_html += f"""
        <tr>
          <td>{tstr}</td>
          <td>{r['open']:.{dec}f}</td><td>{r['high']:.{dec}f}</td>
          <td>{r['low']:.{dec}f}</td><td>{r['close']:.{dec}f}</td>
          <td class="fp-buy">{r['buy_vol']:,.0f}</td>
          <td class="fp-sell">{r['sell_vol']:,.0f}</td>
          <td class="{dcls}">{dlt:+,.0f}</td>
          <td>{r['volume']:,.0f}</td>
        </tr>"""
    st.markdown(f"""
    <div class="dc-panel" style="overflow-x:auto;">
      <table class="fp-table">
        <thead><tr>
          <th>TIME</th><th>O</th><th>H</th><th>L</th><th>C</th>
          <th>BUY</th><th>SELL</th><th>DELTA</th><th>VOL</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)

st.caption(
    f"Deepcharts Clone · {yf_sym} · {timeframe} · POC {poc_s} · Structure: {structure_label} · "
    f"Approx OHLC · User: {st.session_state.get('user','')}"
)

if auto:
    time.sleep(rate)
    st.rerun()
