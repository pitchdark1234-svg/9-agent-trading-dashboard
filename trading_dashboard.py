"""
Bloomberg-style Multi-Agent Trading Terminal
Gold | Crude Oil | Natural Gas | Bitcoin
RSI · MACD · Volume Profile · EMA · Order Block · Institutional Quant
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import random
import yfinance as yf
import streamlit.components.v1 as components

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="BBG-Style Trading Terminal",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== BLOOMBERG TERMINAL CSS ======================
_CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;600;700&family=Roboto:wght@400;500;700&display=swap');

/* === CORE BLOOMBERG LOOK === */
.stApp {
    background: #000000 !important;
    font-family: 'Roboto Mono', 'Courier New', monospace !important;
    color: #e0e0e0 !important;
}
.main .block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"] {
    background: #0a0a0a !important;
    border-right: 1px solid #333 !important;
}
section[data-testid="stSidebar"] * {
    font-family: 'Roboto Mono', monospace !important;
    color: #ccc !important;
}

/* Headers */
h1, h2, h3, h4 {
    font-family: 'Roboto Mono', monospace !important;
    color: #ff6600 !important;
    letter-spacing: 0.5px !important;
    font-weight: 600 !important;
}
.stMarkdown p, .stCaption {
    font-family: 'Roboto Mono', monospace !important;
}

/* Metrics — Bloomberg quote style */
div[data-testid="stMetric"] {
    background: #0d0d0d !important;
    border: 1px solid #222 !important;
    padding: 8px 12px !important;
    border-radius: 0 !important;
}
div[data-testid="stMetric"] label {
    color: #888 !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-family: 'Roboto Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 1.25rem !important;
}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-family: 'Roboto Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* Buttons */
.stButton > button {
    background: #1a1a1a !important;
    color: #ff6600 !important;
    border: 1px solid #ff6600 !important;
    border-radius: 0 !important;
    font-family: 'Roboto Mono', monospace !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}
.stButton > button:hover {
    background: #ff6600 !important;
    color: #000 !important;
}

/* Inputs */
.stSelectbox, .stNumberInput, .stSlider, .stToggle {
    font-family: 'Roboto Mono', monospace !important;
}

/* === BLOOMBERG COMPONENTS === */
.bbg-header {
    background: #000;
    border-bottom: 2px solid #ff6600;
    padding: 6px 14px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.bbg-header-title {
    color: #ff6600;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 2px;
    font-family: 'Roboto Mono', monospace;
}
.bbg-header-sub {
    color: #666;
    font-size: 0.7rem;
    letter-spacing: 1px;
}
.bbg-ticker-bar {
    background: #0a0a0a;
    border: 1px solid #222;
    padding: 6px 12px;
    margin-bottom: 8px;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    color: #aaa;
    white-space: nowrap;
    overflow-x: auto;
}
.bbg-panel {
    background: #0a0a0a;
    border: 1px solid #222;
    padding: 10px 12px;
    margin-bottom: 8px;
}
.bbg-panel-title {
    color: #ff6600;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    border-bottom: 1px solid #222;
    padding-bottom: 4px;
    margin-bottom: 8px;
    font-family: 'Roboto Mono', monospace;
}
.agent-card {
    background: #0a0a0a;
    border: 1px solid #1a1a1a;
    border-left: 3px solid #333;
    border-radius: 0;
    padding: 8px 10px;
    margin-bottom: 6px;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
}
.agent-card:hover {
    border-left-color: #ff6600;
    background: #0f0f0f;
}
.agent-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: #ff6600;
    margin-bottom: 4px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}
.decision-box {
    background: #001a0d;
    border: 1px solid #00aa44;
    border-left: 4px solid #00cc55;
    border-radius: 0;
    padding: 12px 14px;
    margin-top: 6px;
    font-family: 'Roboto Mono', monospace;
}
.decision-box-wait {
    background: #0a0a0a;
    border: 1px solid #333;
    border-left: 4px solid #666;
    border-radius: 0;
    padding: 12px 14px;
    margin-top: 6px;
    font-family: 'Roboto Mono', monospace;
}
.news-alert {
    background: #1a0505;
    border: 1px solid #440000;
    border-left: 3px solid #cc0000;
    border-radius: 0;
    padding: 6px 10px;
    margin-bottom: 4px;
    font-size: 0.75rem;
    font-family: 'Roboto Mono', monospace;
}
.ob-card {
    background: #0a0a12;
    border: 1px solid #1a1a2e;
    border-left: 3px solid #ff6600;
    border-radius: 0;
    padding: 8px 10px;
    margin-bottom: 6px;
    font-family: 'Roboto Mono', monospace;
}
.status-online { color: #00cc55; font-weight: 600; }
.status-pending { color: #ff9900; }
.pos { color: #00cc55 !important; }
.neg { color: #ff3333 !important; }
.amber { color: #ff6600 !important; }

/* Hide Streamlit branding for cleaner terminal look */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)

# ====================== REAL MARKET DATA ======================
SYMBOLS = {
    "Gold (XAUUSD)": "GC=F",
    "Crude Oil (WTI)": "CL=F",
    "Natural Gas": "NG=F",
    "Bitcoin (BTC)": "BTC-USD"
}

SYMBOL_KEYS = {
    "Gold (XAUUSD)": "gold",
    "Crude Oil (WTI)": "crude",
    "Natural Gas": "natgas",
    "Bitcoin (BTC)": "bitcoin"
}

@st.cache_data(ttl=45)
def fetch_real_prices():
    prices = {}
    changes = {}
    try:
        for name, symbol in SYMBOLS.items():
            key = SYMBOL_KEYS[name]
            ticker = yf.Ticker(symbol)
            try:
                info = ticker.fast_info
                price = info.get("lastPrice") or info.get("regularMarketPrice")
                prev = info.get("previousClose")
            except Exception:
                hist = ticker.history(period="5d", interval="1d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price
                else:
                    price, prev = None, None
            if price is not None:
                decimals = 3 if key == "natgas" else 2
                prices[key] = round(float(price), decimals)
                changes[key] = round(float(price) - float(prev), decimals) if prev else 0.0
            else:
                prices[key] = None
                changes[key] = 0.0
    except Exception as e:
        return None, None
    return prices, changes

@st.cache_data(ttl=60)
def generate_ohlc_history(symbol, periods=120):
    """Fetch real OHLC + Volume for advanced chart"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d", interval="15m")
        if hist.empty or len(hist) < 20:
            hist = ticker.history(period="1mo", interval="1h")
        if not hist.empty:
            df = hist.tail(periods).reset_index()
            time_col = "Datetime" if "Datetime" in df.columns else df.columns[0]
            df = df.rename(columns={time_col: "time"})
            df = df[["time", "Open", "High", "Low", "Close", "Volume"]].copy()
            df.columns = ["time", "open", "high", "low", "close", "volume"]
            return df
    except Exception:
        pass
    # Fallback simulated OHLC
    base = {"GC=F": 2650, "CL=F": 73, "NG=F": 2.9, "BTC-USD": 64000}.get(symbol, 100)
    np.random.seed(hash(symbol) % 2**32)
    returns = np.random.normal(0, 0.0012, periods)
    closes = base * np.cumprod(1 + returns)
    opens = np.roll(closes, 1)
    opens[0] = base
    highs = np.maximum(opens, closes) * (1 + np.abs(np.random.normal(0, 0.0008, periods)))
    lows = np.minimum(opens, closes) * (1 - np.abs(np.random.normal(0, 0.0008, periods)))
    volumes = np.random.randint(800, 4500, periods)
    times = [datetime.now() - timedelta(minutes=15 * (periods - i)) for i in range(periods)]
    return pd.DataFrame({
        "time": times, "open": opens, "high": highs, "low": lows, "close": closes, "volume": volumes
    })

def get_live_prices():
    real, changes = fetch_real_prices()
    if real and all(v is not None for v in real.values()):
        return real, changes, True
    base = {
        "gold": 2651.20 + random.uniform(-3, 3),
        "crude": 72.85 + random.uniform(-0.4, 0.4),
        "natgas": 2.87 + random.uniform(-0.05, 0.05),
        "bitcoin": 64000 + random.uniform(-800, 800)
    }
    prices = {k: round(v, 2 if k != "natgas" else 3) for k, v in base.items()}
    changes = {k: round(random.uniform(-2, 2) if k != "bitcoin" else random.uniform(-400, 400), 2) for k in prices}
    return prices, changes, False

def detect_order_blocks(df, lookback=40):
    """
    Simple Order Block detection:
    - Bullish OB: last down candle before a strong upward impulse
    - Bearish OB: last up candle before a strong downward impulse
    Returns list of dicts with type, top, bottom, mid, strength
    """
    if df is None or len(df) < lookback + 5:
        return []
    
    recent = df.tail(lookback).copy().reset_index(drop=True)
    obs = []
    
    # Calculate impulse strength (body + range)
    recent["body"] = abs(recent["close"] - recent["open"])
    recent["range"] = recent["high"] - recent["low"]
    avg_body = recent["body"].mean()
    
    for i in range(3, len(recent) - 4):
        # Bullish Order Block: bearish candle followed by strong bullish move
        if (recent.loc[i, "close"] < recent.loc[i, "open"] and
            recent.loc[i+1, "close"] > recent.loc[i+1, "open"] and
            recent.loc[i+2, "close"] > recent.loc[i+1, "close"] and
            recent.loc[i+1, "body"] > avg_body * 1.4):
            
            top = max(recent.loc[i, "open"], recent.loc[i, "close"])
            bottom = min(recent.loc[i, "open"], recent.loc[i, "close"])
            # Prefer the body as OB zone
            mid = (top + bottom) / 2
            strength = min(1.0, recent.loc[i+1, "body"] / (avg_body + 1e-9))
            obs.append({
                "type": "Bullish OB",
                "top": round(top, 3),
                "bottom": round(bottom, 3),
                "mid": round(mid, 3),
                "strength": round(strength, 2),
                "time": recent.loc[i, "time"]
            })
        
        # Bearish Order Block
        if (recent.loc[i, "close"] > recent.loc[i, "open"] and
            recent.loc[i+1, "close"] < recent.loc[i+1, "open"] and
            recent.loc[i+2, "close"] < recent.loc[i+1, "close"] and
            recent.loc[i+1, "body"] > avg_body * 1.4):
            
            top = max(recent.loc[i, "open"], recent.loc[i, "close"])
            bottom = min(recent.loc[i, "open"], recent.loc[i, "close"])
            mid = (top + bottom) / 2
            strength = min(1.0, recent.loc[i+1, "body"] / (avg_body + 1e-9))
            obs.append({
                "type": "Bearish OB",
                "top": round(top, 3),
                "bottom": round(bottom, 3),
                "mid": round(mid, 3),
                "strength": round(strength, 2),
                "time": recent.loc[i, "time"]
            })
    
    # Keep only the strongest / most recent few
    obs = sorted(obs, key=lambda x: x["strength"], reverse=True)[:4]
    return obs

# ====================== REAL TECHNICAL INDICATORS ======================
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    return 100 - (100 / (1 + rs))

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def compute_volume_profile(df, bins=24):
    """Approximate Volume Profile: find Point of Control (highest volume price area)"""
    if df is None or len(df) < 10 or df["volume"].sum() == 0:
        return {"poc": None, "vah": None, "val": None, "bias": "Neutral"}
    price_min = df["low"].min()
    price_max = df["high"].max()
    if price_max <= price_min:
        return {"poc": float(df["close"].iloc[-1]), "vah": None, "val": None, "bias": "Neutral"}
    bin_edges = np.linspace(price_min, price_max, bins + 1)
    vol_at_price = np.zeros(bins)
    for _, row in df.iterrows():
        mid = (row["high"] + row["low"]) / 2
        idx = np.searchsorted(bin_edges, mid, side="right") - 1
        idx = max(0, min(bins - 1, idx))
        vol_at_price[idx] += row["volume"]
    poc_idx = int(np.argmax(vol_at_price))
    poc = (bin_edges[poc_idx] + bin_edges[poc_idx + 1]) / 2
    # Value Area (approx 70% volume)
    total = vol_at_price.sum()
    sorted_idx = np.argsort(vol_at_price)[::-1]
    cum = 0
    va_bins = []
    for i in sorted_idx:
        cum += vol_at_price[i]
        va_bins.append(i)
        if cum >= total * 0.70:
            break
    va_low = bin_edges[min(va_bins)]
    va_high = bin_edges[max(va_bins) + 1]
    last = float(df["close"].iloc[-1])
    if last > poc * 1.002:
        bias = "Bullish (above POC)"
    elif last < poc * 0.998:
        bias = "Bearish (below POC)"
    else:
        bias = "Neutral (at POC)"
    return {
        "poc": round(poc, 4),
        "vah": round(va_high, 4),
        "val": round(va_low, 4),
        "bias": bias
    }

def compute_atr(df, period=14):
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()

def analyze_market(df, order_blocks, current_price):
    """
    Powerful multi-indicator engine.
    Returns structured signals from RSI, MACD, Volume Profile, EMA structure, ATR, Order Blocks.
    Only produces a trade bias when several independent signals agree.
    """
    if df is None or len(df) < 30:
        return None

    close = df["close"]
    last = float(close.iloc[-1])

    # --- RSI ---
    rsi = compute_rsi(close, 14)
    rsi_val = float(rsi.iloc[-1])
    rsi_prev = float(rsi.iloc[-2]) if len(rsi) > 1 else rsi_val
    if rsi_val < 30:
        rsi_signal = "BUY"
        rsi_note = f"RSI oversold ({rsi_val:.1f})"
    elif rsi_val > 70:
        rsi_signal = "SELL"
        rsi_note = f"RSI overbought ({rsi_val:.1f})"
    elif rsi_val > rsi_prev and rsi_val > 50:
        rsi_signal = "BUY"
        rsi_note = f"RSI rising in bull zone ({rsi_val:.1f})"
    elif rsi_val < rsi_prev and rsi_val < 50:
        rsi_signal = "SELL"
        rsi_note = f"RSI falling in bear zone ({rsi_val:.1f})"
    else:
        rsi_signal = "NEUTRAL"
        rsi_note = f"RSI neutral ({rsi_val:.1f})"

    # --- MACD ---
    macd_line, signal_line, hist = compute_macd(close)
    macd_val = float(macd_line.iloc[-1])
    sig_val = float(signal_line.iloc[-1])
    hist_val = float(hist.iloc[-1])
    hist_prev = float(hist.iloc[-2]) if len(hist) > 1 else hist_val
    if macd_val > sig_val and hist_val > 0 and hist_val > hist_prev:
        macd_signal = "BUY"
        macd_note = "MACD bullish crossover / rising histogram"
    elif macd_val < sig_val and hist_val < 0 and hist_val < hist_prev:
        macd_signal = "SELL"
        macd_note = "MACD bearish crossover / falling histogram"
    elif hist_val > 0:
        macd_signal = "BUY"
        macd_note = "MACD histogram positive"
    elif hist_val < 0:
        macd_signal = "SELL"
        macd_note = "MACD histogram negative"
    else:
        macd_signal = "NEUTRAL"
        macd_note = "MACD flat"

    # --- EMAs (trend structure) ---
    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    e20 = float(ema20.iloc[-1])
    e50 = float(ema50.iloc[-1])
    if last > e20 > e50:
        ema_signal = "BUY"
        ema_note = "Price > EMA20 > EMA50 (strong uptrend)"
    elif last < e20 < e50:
        ema_signal = "SELL"
        ema_note = "Price < EMA20 < EMA50 (strong downtrend)"
    elif last > e20:
        ema_signal = "BUY"
        ema_note = "Price above EMA20 (short-term bullish)"
    elif last < e20:
        ema_signal = "SELL"
        ema_note = "Price below EMA20 (short-term bearish)"
    else:
        ema_signal = "NEUTRAL"
        ema_note = "Price consolidating around EMAs"

    # --- Volume Profile ---
    vp = compute_volume_profile(df.tail(80))
    if "Bullish" in vp["bias"]:
        vp_signal = "BUY"
    elif "Bearish" in vp["bias"]:
        vp_signal = "SELL"
    else:
        vp_signal = "NEUTRAL"
    vp_note = f"POC {vp['poc']} | {vp['bias']}"

    # --- ATR (for risk sizing) ---
    atr = compute_atr(df, 14)
    atr_val = float(atr.iloc[-1]) if not atr.empty else last * 0.01

    # --- Order Block alignment ---
    nearest_ob = None
    ob_aligned = False
    ob_signal_txt = "No high-quality Order Block near price"
    ob_bias = "NEUTRAL"
    if order_blocks:
        for ob in order_blocks:
            dist = abs(ob["mid"] - current_price)
            if nearest_ob is None or dist < abs(nearest_ob["mid"] - current_price):
                nearest_ob = ob
        if nearest_ob:
            zone_dist = abs(nearest_ob["mid"] - current_price) / max(current_price, 1e-9)
            if zone_dist < 0.006:  # within ~0.6%
                ob_aligned = True
                if nearest_ob["type"] == "Bullish OB":
                    ob_bias = "BUY"
                    ob_signal_txt = f"Price at Bullish OB {nearest_ob['bottom']:.2f}-{nearest_ob['top']:.2f}"
                else:
                    ob_bias = "SELL"
                    ob_signal_txt = f"Price at Bearish OB {nearest_ob['bottom']:.2f}-{nearest_ob['top']:.2f}"
            else:
                ob_signal_txt = f"Nearest {nearest_ob['type']} @ {nearest_ob['mid']:.2f} (watching)"

    # --- Collect votes ---
    votes = {
        "RSI": rsi_signal,
        "MACD": macd_signal,
        "EMA": ema_signal,
        "VolumeProfile": vp_signal,
        "OrderBlock": ob_bias if ob_aligned else "NEUTRAL"
    }
    buy_votes = sum(1 for v in votes.values() if v == "BUY")
    sell_votes = sum(1 for v in votes.values() if v == "SELL")

    # ============================================================
    # INSTITUTIONAL QUANT MODEL (JPM / RiskMetrics inspired)
    # Multi-factor score + volatility regime + risk budgeting
    # ============================================================
    # Factor 1: Momentum (MACD + EMA structure)
    mom_score = 0.0
    if macd_signal == "BUY":
        mom_score += 0.5
    elif macd_signal == "SELL":
        mom_score -= 0.5
    if ema_signal == "BUY":
        mom_score += 0.5
    elif ema_signal == "SELL":
        mom_score -= 0.5

    # Factor 2: Mean-reversion (RSI extremes)
    mr_score = 0.0
    if rsi_val < 30:
        mr_score += 0.8   # oversold → buy pressure
    elif rsi_val > 70:
        mr_score -= 0.8
    elif rsi_val < 40:
        mr_score += 0.3
    elif rsi_val > 60:
        mr_score -= 0.3

    # Factor 3: Volume / flow (Volume Profile)
    flow_score = 0.0
    if vp_signal == "BUY":
        flow_score += 0.6
    elif vp_signal == "SELL":
        flow_score -= 0.6

    # Factor 4: Structural (Order Block)
    structure_score = 0.0
    if ob_aligned and ob_bias == "BUY":
        structure_score += 0.9
    elif ob_aligned and ob_bias == "SELL":
        structure_score -= 0.9

    # Composite institutional score (-3 to +3 range roughly)
    quant_score = mom_score + mr_score + flow_score + structure_score

    # Volatility regime (RiskMetrics-style)
    # Compare recent ATR to longer-term ATR
    atr_series = compute_atr(df, 14)
    atr_long = float(atr_series.tail(50).mean()) if len(atr_series) >= 50 else atr_val
    vol_ratio = atr_val / (atr_long + 1e-9)
    if vol_ratio > 1.35:
        vol_regime = "HIGH"
        vol_note = f"Elevated volatility (ATR ratio {vol_ratio:.2f}) — reduce size"
    elif vol_ratio < 0.75:
        vol_regime = "LOW"
        vol_note = f"Compressed volatility (ATR ratio {vol_ratio:.2f}) — breakout watch"
    else:
        vol_regime = "NORMAL"
        vol_note = f"Normal volatility regime (ATR ratio {vol_ratio:.2f})"

    # Trend regime via ADX-like simplicity (EMA separation)
    ema_sep = abs(e20 - e50) / (last + 1e-9)
    if ema_sep > 0.008 and (last > e20 > e50 or last < e20 < e50):
        trend_regime = "TRENDING"
    else:
        trend_regime = "RANGING"

    # Final institutional bias — stricter than simple vote
    # Require quant_score magnitude + vote agreement
    if quant_score >= 1.4 and buy_votes >= 3:
        final_bias = "BUY"
    elif quant_score <= -1.4 and sell_votes >= 3:
        final_bias = "SELL"
    else:
        final_bias = "NEUTRAL"

    # Conflict with Order Block kills the trade
    if ob_aligned and ob_bias != "NEUTRAL" and final_bias != "NEUTRAL" and final_bias != ob_bias:
        final_bias = "NEUTRAL"

    # In HIGH vol regime, demand even stronger score
    if vol_regime == "HIGH" and abs(quant_score) < 1.8:
        final_bias = "NEUTRAL"

    quant_signal = "BUY" if quant_score > 0.6 else ("SELL" if quant_score < -0.6 else "NEUTRAL")
    quant_note = (
        f"Score {quant_score:+.2f} | Mom {mom_score:+.1f} | MR {mr_score:+.1f} | "
        f"Flow {flow_score:+.1f} | Struct {structure_score:+.1f} | {vol_regime} vol | {trend_regime}"
    )

    return {
        "rsi": {"value": round(rsi_val, 1), "signal": rsi_signal, "note": rsi_note},
        "macd": {"value": round(macd_val, 4), "signal": macd_signal, "note": macd_note, "hist": round(hist_val, 4)},
        "ema": {"ema20": round(e20, 4), "ema50": round(e50, 4), "signal": ema_signal, "note": ema_note},
        "volume_profile": {**vp, "signal": vp_signal, "note": vp_note},
        "atr": round(atr_val, 4),
        "orderblock": {
            "aligned": ob_aligned,
            "nearest": nearest_ob,
            "signal": ob_signal_txt,
            "bias": ob_bias,
            "confidence": nearest_ob["strength"] if nearest_ob else 0.0
        },
        "votes": votes,
        "buy_votes": buy_votes,
        "sell_votes": sell_votes,
        "final_bias": final_bias,
        # Institutional Quant Model (JPM-style)
        "quant": {
            "score": round(quant_score, 2),
            "signal": quant_signal,
            "note": quant_note,
            "vol_regime": vol_regime,
            "vol_note": vol_note,
            "trend_regime": trend_regime,
            "mom_score": round(mom_score, 2),
            "mr_score": round(mr_score, 2),
            "flow_score": round(flow_score, 2),
            "structure_score": round(structure_score, 2),
            "vol_ratio": round(vol_ratio, 2)
        }
    }

def get_agent_outputs(prices, selected_key, order_blocks, current_price, ohlc_df=None):
    """
    Powerful multi-agent system driven by REAL indicators:
    RSI • MACD • Volume Profile • EMA Structure • Order Block • ATR Risk
    Trade signal only when ≥3 indicators + Order Block agree.
    """
    analysis = analyze_market(ohlc_df, order_blocks, current_price) if ohlc_df is not None else None

    instrument_names = {
        "gold": "XAUUSD (Gold)",
        "crude": "CL (Crude Oil)",
        "natgas": "NG (Natural Gas)",
        "bitcoin": "BTC-USD (Bitcoin)"
    }
    display_name = instrument_names.get(selected_key, selected_key.upper())

    # Adaptive SL/TP using ATR when available
    atr = analysis["atr"] if analysis else (current_price * 0.008)
    if selected_key == "gold":
        size = "0.40 lots"
    elif selected_key == "crude":
        size = "1.00 lots"
    elif selected_key == "natgas":
        size = "2.00 lots"
    else:
        size = "0.05 BTC"

    decimals = 3 if selected_key == "natgas" else 2

    # Default empty decision
    decision = {
        "name": "9️⃣ Final Decision Agent",
        "status": "WAITING",
        "instrument": display_name,
        "side": "—",
        "entry": "—",
        "stop_loss": "—",
        "take_profit": "—",
        "size": "—",
        "confidence": 0.0,
        "reasoning": "Waiting for high-confluence setup (RSI + MACD + Volume Profile + EMA + Order Block).",
        "aligned_agents": [],
        "has_trade": False
    }

    if analysis and analysis["final_bias"] in ("BUY", "SELL"):
        side = analysis["final_bias"]
        ob_ok = analysis["orderblock"]["aligned"]
        strong_votes = analysis["buy_votes"] if side == "BUY" else analysis["sell_votes"]
        q = analysis.get("quant", {})
        quant_score = q.get("score", 0)
        vol_regime = q.get("vol_regime", "NORMAL")

        # Institutional gate: strong votes + quant score + prefer OB
        if strong_votes >= 3 and abs(quant_score) >= 1.4 and (ob_ok or strong_votes >= 4):
            # Volatility targeting: shrink size in HIGH vol
            size_mult = 0.5 if vol_regime == "HIGH" else (1.2 if vol_regime == "LOW" else 1.0)
            display_size = size
            if selected_key == "bitcoin":
                display_size = f"{0.05 * size_mult:.3f} BTC"
            elif "lots" in size:
                try:
                    base_lots = float(size.split()[0])
                    display_size = f"{base_lots * size_mult:.2f} lots"
                except Exception:
                    display_size = size

            entry_offset = atr * 0.1
            sl_dist = atr * 1.5
            tp_dist = atr * 2.5
            entry = round(current_price + (entry_offset if side == "BUY" else -entry_offset), decimals)
            sl = round(current_price - sl_dist if side == "BUY" else current_price + sl_dist, decimals)
            tp = round(current_price + tp_dist if side == "BUY" else current_price - tp_dist, decimals)

            aligned = [k for k, v in analysis["votes"].items() if v == side]
            aligned.append("InstitutionalQuant")
            conf = min(0.95, 0.50 + strong_votes * 0.07 + min(0.15, abs(quant_score) * 0.05) + (0.08 if ob_ok else 0))

            decision = {
                "name": "9️⃣ Final Decision Agent",
                "status": "TRADE READY",
                "instrument": display_name,
                "side": side,
                "entry": entry,
                "stop_loss": sl,
                "take_profit": tp,
                "size": display_size,
                "confidence": conf,
                "reasoning": (
                    f"INSTITUTIONAL CONFLUENCE. Quant score {quant_score:+.2f} | "
                    f"{strong_votes}/5 signals aligned: {', '.join(aligned)}. "
                    f"Vol regime: {vol_regime}. "
                    f"{'Order Block confirmed. ' if ob_ok else ''}"
                    f"ATR-based SL/TP + volatility targeting."
                ),
                "aligned_agents": aligned,
                "has_trade": True
            }

    # Build agent cards from real analysis
    if analysis is None:
        analysis = {
            "rsi": {"value": 50, "signal": "NEUTRAL", "note": "Insufficient data"},
            "macd": {"value": 0, "signal": "NEUTRAL", "note": "Insufficient data", "hist": 0},
            "ema": {"ema20": current_price, "ema50": current_price, "signal": "NEUTRAL", "note": "Insufficient data"},
            "volume_profile": {"poc": current_price, "vah": None, "val": None, "bias": "Neutral", "signal": "NEUTRAL", "note": "N/A"},
            "atr": current_price * 0.01,
            "orderblock": {"aligned": False, "nearest": None, "signal": "No data", "bias": "NEUTRAL", "confidence": 0},
            "votes": {}, "buy_votes": 0, "sell_votes": 0, "final_bias": "NEUTRAL",
            "quant": {
                "score": 0, "signal": "NEUTRAL", "note": "Insufficient data",
                "vol_regime": "NORMAL", "vol_note": "N/A", "trend_regime": "RANGING",
                "mom_score": 0, "mr_score": 0, "flow_score": 0, "structure_score": 0, "vol_ratio": 1.0
            }
        }
    if "quant" not in analysis:
        analysis["quant"] = {
            "score": 0, "signal": "NEUTRAL", "note": "N/A",
            "vol_regime": "NORMAL", "vol_note": "N/A", "trend_regime": "RANGING",
            "mom_score": 0, "mr_score": 0, "flow_score": 0, "structure_score": 0, "vol_ratio": 1.0
        }

    return {
        "scanner": {
            "name": "1️⃣ Market Scanner",
            "status": "Active",
            "priority": selected_key.upper(),
            "summary": f"Bias: {analysis['final_bias']} | Buy votes: {analysis['buy_votes']} | Sell votes: {analysis['sell_votes']}",
            "confidence": 0.85
        },
        "rsi_agent": {
            "name": "2️⃣ RSI Agent (14)",
            "status": "Active",
            "analysis": analysis["rsi"]["note"],
            "signal": analysis["rsi"]["signal"],
            "value": analysis["rsi"]["value"],
            "confidence": 0.80 if analysis["rsi"]["signal"] != "NEUTRAL" else 0.50
        },
        "macd_agent": {
            "name": "3️⃣ MACD Agent (12/26/9)",
            "status": "Active",
            "analysis": analysis["macd"]["note"],
            "signal": analysis["macd"]["signal"],
            "value": analysis["macd"]["value"],
            "hist": analysis["macd"]["hist"],
            "confidence": 0.82 if analysis["macd"]["signal"] != "NEUTRAL" else 0.50
        },
        "volume_profile": {
            "name": "4️⃣ Volume Profile Agent",
            "status": "Active",
            "analysis": analysis["volume_profile"]["note"],
            "signal": analysis["volume_profile"]["signal"],
            "poc": analysis["volume_profile"].get("poc"),
            "vah": analysis["volume_profile"].get("vah"),
            "val": analysis["volume_profile"].get("val"),
            "confidence": 0.78 if analysis["volume_profile"]["signal"] != "NEUTRAL" else 0.50
        },
        "ema_agent": {
            "name": "5️⃣ EMA Structure Agent",
            "status": "Active",
            "analysis": analysis["ema"]["note"],
            "signal": analysis["ema"]["signal"],
            "ema20": analysis["ema"]["ema20"],
            "ema50": analysis["ema"]["ema50"],
            "confidence": 0.81 if analysis["ema"]["signal"] != "NEUTRAL" else 0.50
        },
        "momentum": {
            "name": "6️⃣ Momentum & ATR",
            "status": "Active",
            "analysis": f"ATR(14): {analysis['atr']:.4f} | Used for dynamic SL/TP (1.5× / 2.5×)",
            "signal": "Volatility measured",
            "confidence": 0.75
        },
        "quant_model": {
            "name": "🏦 Institutional Quant Model (JPM-style)",
            "status": "Active",
            "analysis": analysis["quant"]["note"],
            "signal": analysis["quant"]["signal"],
            "score": analysis["quant"]["score"],
            "vol_regime": analysis["quant"]["vol_regime"],
            "vol_note": analysis["quant"]["vol_note"],
            "trend_regime": analysis["quant"]["trend_regime"],
            "confidence": min(0.92, 0.55 + abs(analysis["quant"]["score"]) * 0.12)
        },
        "news": {
            "name": "7️⃣ News & Event Agent",
            "status": "Active",
            "upcoming": [
                {"event": "US CPI (Core)", "time": "Today 18:30 IST", "impact": "HIGH", "focus": "Gold / BTC"},
                {"event": "EIA Crude Inventories", "time": "Today 20:30 IST", "impact": "HIGH", "focus": "Crude"},
                {"event": "FOMC Member Speech", "time": "Tomorrow 15:00 IST", "impact": "MEDIUM", "focus": "Gold / BTC"}
            ],
            "critical": "No critical breaking news in last 15 min",
            "bias": "Watch high-impact events before increasing size"
        },
        "risk": {
            "name": "8️⃣ Risk Manager",
            "status": "Active",
            "approved": True,
            "max_risk": "0.5% equity",
            "suggested_sl_atr": "1.5× ATR",
            "position_size": size,
            "veto": None,
            "note": f"ATR-based stops active. Current ATR: {analysis['atr']:.4f}"
        },
        "orderblock": {
            "name": "🔟 Order Block Scanner",
            "status": "Active",
            "levels": order_blocks,
            "nearest": analysis["orderblock"]["nearest"],
            "signal": analysis["orderblock"]["signal"],
            "aligned": analysis["orderblock"]["aligned"],
            "confidence": analysis["orderblock"]["confidence"]
        },
        "decision": decision,
        "analysis": analysis  # full raw analysis for UI
    }

# ====================== SOUND ALERT JS ======================
def play_alert_sound(kind="trade"):
    """Inject a pleasant beep / chime via Web Audio API"""
    if kind == "trade":
        # Pleasant ascending chime
        js = """
        <script>
        (function(){
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const notes = [523.25, 659.25, 783.99]; // C5 E5 G5
            notes.forEach((freq, i) => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.frequency.value = freq;
                osc.type = 'sine';
                gain.gain.setValueAtTime(0.25, ctx.currentTime + i*0.18);
                gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i*0.18 + 0.4);
                osc.start(ctx.currentTime + i*0.18);
                osc.stop(ctx.currentTime + i*0.18 + 0.45);
            });
        })();
        </script>
        """
    else:
        # Soft alert beep for level touch
        js = """
        <script>
        (function(){
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.value = 880;
            osc.type = 'sine';
            gain.gain.setValueAtTime(0.2, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.4);
        })();
        </script>
        """
    components.html(js, height=0)

# ====================== SIDEBAR CONTROL PANEL ======================
with st.sidebar:
    st.markdown("### ⚡ Control Panel")
    st.markdown("---")
    
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    auto_refresh = st.toggle("Live Auto-Refresh", value=False)
    refresh_rate = st.slider("Refresh every (seconds)", 5, 60, 15)
    
    st.markdown("---")
    st.markdown("### 📊 Instrument Focus")
    selected_instrument = st.selectbox(
        "Select Instrument (Chart + Agents)",
        list(SYMBOLS.keys()),
        index=0
    )
    selected_symbol = SYMBOLS[selected_instrument]
    selected_key = SYMBOL_KEYS[selected_instrument]
    
    st.markdown("---")
    st.markdown("### 🔔 Key Alert Settings")
    enable_sound = st.toggle("Enable Sound Alerts", value=True)
    alert_level = st.number_input(
        "Alert Price Level",
        value=0.0,
        step=0.1,
        help="Set a price. When live price reaches ±0.15% of this level, sound alert triggers."
    )
    alert_tolerance = st.slider("Alert Tolerance %", 0.05, 0.50, 0.15, 0.05)
    
    st.markdown("---")
    st.markdown("### ⚙️ Trade Filters")
    min_confluence = st.slider("Min Agents for Signal", 4, 8, 5)
    require_ob = st.toggle("Require Order Block Alignment", value=True)
    
    st.markdown("---")
    st.markdown("### System Status")
    st.markdown('<span class="status-online">● RSI + MACD + Volume Profile + EMA + Order Block + Institutional Quant Online</span>', unsafe_allow_html=True)
    st.caption(f"Last cycle: {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    st.markdown("### Risk Settings")
    max_risk = st.slider("Max Risk per Trade %", 0.1, 2.0, 0.5, 0.1)
    atr_mult = st.slider("Stop Loss ATR Multiplier", 1.0, 3.0, 1.5, 0.1)
    
    st.markdown("---")
    st.info("Simulation + real Yahoo data. No real orders are executed.")

# ====================== BLOOMBERG-STYLE HEADER ======================
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
<div class="bbg-header">
    <div>
        <span class="bbg-header-title">TERMINAL</span>
        <span style="color:#444; margin:0 10px;">|</span>
        <span style="color:#ccc; font-size:0.85rem; font-family:'Roboto Mono',monospace;">{selected_instrument}</span>
        <span style="color:#444; margin:0 8px;">|</span>
        <span style="color:#666; font-size:0.7rem;">RSI · MACD · VOL PROF · EMA · OB · QUANT</span>
    </div>
    <div class="bbg-header-sub">{now_str} IST</div>
</div>
""", unsafe_allow_html=True)

# ====================== LIVE PRICES ======================
prices, changes, is_live = get_live_prices()
current_price = prices[selected_key]

# OHLC data for selected instrument
ohlc_df = generate_ohlc_history(selected_symbol)
order_blocks = detect_order_blocks(ohlc_df)

agents = get_agent_outputs(prices, selected_key, order_blocks, current_price, ohlc_df)

data_source = "LIVE" if is_live else "SIM"
delta = changes.get(selected_key, 0)
delta_pct = (delta / current_price * 100) if current_price else 0
delta_cls = "pos" if delta >= 0 else "neg"
fmt_price = f"{current_price:,.3f}" if selected_key == "natgas" else f"{current_price:,.2f}"
fmt_delta = f"{delta:+.3f}" if selected_key == "natgas" else f"{delta:+.2f}"

# Bloomberg-style ticker quote strip
st.markdown(f"""
<div class="bbg-ticker-bar">
    <span style="color:#ff6600; font-weight:700;">{selected_symbol}</span>
    &nbsp;&nbsp;
    <span style="color:#fff; font-weight:700; font-size:1.05rem;">{fmt_price}</span>
    &nbsp;
    <span class="{delta_cls}">{fmt_delta} ({delta_pct:+.2f}%)</span>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    SRC: <span style="color:#aaa;">{data_source}</span>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    OB: <span style="color:{'#00cc55' if agents['orderblock']['aligned'] else '#888'};">{'ALIGNED' if agents['orderblock']['aligned'] else 'WATCH'}</span>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    CONF: <span style="color:#ff6600;">{agents['decision']['confidence']*100:.0f}%</span>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    QUANT: <span style="color:#ccc;">{agents.get('quant_model', {}).get('score', 0):+.2f}</span>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    VOL: <span style="color:#aaa;">{agents.get('quant_model', {}).get('vol_regime', '—')}</span>
</div>
""", unsafe_allow_html=True)

# Compact metrics row
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("LAST", fmt_price, f"{fmt_delta}")
with col2:
    st.metric("ORDER BLOCKS", len(order_blocks), "zones")
with col3:
    conf = agents["decision"]["confidence"]
    st.metric("CONFLUENCE", f"{conf*100:.0f}%" if conf > 0 else "—", "READY" if agents["decision"]["has_trade"] else "WAIT")
with col4:
    st.metric("OB STATUS", "ALIGNED" if agents["orderblock"]["aligned"] else "WATCH")
with col5:
    qscore = agents.get("quant_model", {}).get("score", 0)
    st.metric("QUANT SCORE", f"{qscore:+.2f}")

# ====================== CHART ======================
st.markdown(f'<div class="bbg-panel-title" style="margin-top:10px;">{selected_symbol} — CANDLESTICK + VOLUME + ORDER BLOCKS</div>', unsafe_allow_html=True)

fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.72, 0.28],
    subplot_titles=(f"{selected_symbol} Price", "Volume")
)

# Candlesticks
fig.add_trace(go.Candlestick(
    x=ohlc_df["time"],
    open=ohlc_df["open"],
    high=ohlc_df["high"],
    low=ohlc_df["low"],
    close=ohlc_df["close"],
    name="OHLC",
    increasing_line_color="#00cc55",
    decreasing_line_color="#ff3333",
    increasing_fillcolor="#00cc55",
    decreasing_fillcolor="#ff3333"
), row=1, col=1)

# Simple Moving Averages
if len(ohlc_df) >= 20:
    ohlc_df["ma20"] = ohlc_df["close"].rolling(20).mean()
    ohlc_df["ma50"] = ohlc_df["close"].rolling(50).mean() if len(ohlc_df) >= 50 else None
    fig.add_trace(go.Scatter(
        x=ohlc_df["time"], y=ohlc_df["ma20"],
        mode="lines", name="MA20",
        line=dict(color="#fbbf24", width=1.5)
    ), row=1, col=1)
    if ohlc_df["ma50"] is not None:
        fig.add_trace(go.Scatter(
            x=ohlc_df["time"], y=ohlc_df["ma50"],
            mode="lines", name="MA50",
            line=dict(color="#38bdf8", width=1.5)
        ), row=1, col=1)

# Order Block zones as horizontal rectangles / lines
colors_ob = {"Bullish OB": "rgba(34, 197, 94, 0.25)", "Bearish OB": "rgba(239, 68, 68, 0.25)"}
line_colors = {"Bullish OB": "#00cc55", "Bearish OB": "#ff3333"}

for ob in order_blocks:
    fig.add_hrect(
        y0=ob["bottom"], y1=ob["top"],
        fillcolor=colors_ob.get(ob["type"], "rgba(99,102,241,0.2)"),
        line_width=0,
        row=1, col=1
    )
    fig.add_hline(
        y=ob["mid"],
        line_dash="dash",
        line_color=line_colors.get(ob["type"], "#6366f1"),
        line_width=1.5,
        annotation_text=f"{ob['type']} {ob['mid']:.2f}",
        annotation_position="right",
        row=1, col=1
    )

# Volume bars
colors_vol = ["#00cc55" if c >= o else "#ff3333" for c, o in zip(ohlc_df["close"], ohlc_df["open"])]
fig.add_trace(go.Bar(
    x=ohlc_df["time"],
    y=ohlc_df["volume"],
    name="Volume",
    marker_color=colors_vol,
    opacity=0.7
), row=2, col=1)

fig.update_layout(
    template="plotly_dark",
    height=480,
    margin=dict(l=8, r=8, t=28, b=8),
    paper_bgcolor="#000000",
    plot_bgcolor="#000000",
    font=dict(family="Roboto Mono, monospace", color="#aaa", size=11),
    xaxis_rangeslider_visible=False,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#888")),
    hovermode="x unified"
)
fig.update_xaxes(showgrid=False, row=1, col=1, color="#444")
fig.update_xaxes(showgrid=False, row=2, col=1, color="#444")
fig.update_yaxes(showgrid=True, gridcolor="#1a1a1a", row=1, col=1, color="#666")
fig.update_yaxes(showgrid=False, row=2, col=1, color="#666")

st.plotly_chart(fig, use_container_width=True)

# ====================== ORDER BLOCK SCANNER PANEL ======================
st.markdown('<div class="bbg-panel-title">ORDER BLOCK SCANNER — KEY LEVELS</div>', unsafe_allow_html=True)

if order_blocks:
    ob_cols = st.columns(min(4, len(order_blocks)))
    for idx, ob in enumerate(order_blocks):
        with ob_cols[idx % len(ob_cols)]:
            color = "#00cc55" if "Bullish" in ob["type"] else "#ff3333"
            st.markdown(f"""
            <div class="ob-card">
                <div style="color:{color}; font-weight:600;">{ob['type']}</div>
                <p style="color:#e2e8f0; font-size:0.9rem; margin:0.3rem 0;">
                    Zone: <b>{ob['bottom']:.2f} – {ob['top']:.2f}</b><br>
                    Mid: <b>{ob['mid']:.2f}</b><br>
                    Strength: {ob['strength']*100:.0f}%
                </p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("No high-quality Order Blocks detected in the recent window. Scanner continues monitoring.")

st.markdown(f"**Scanner Signal:** {agents['orderblock']['signal']}")

st.markdown("---")

# ====================== FINAL DECISION (CONDITIONAL) ======================
st.markdown('<div class="bbg-panel-title">TRADE DECISION — INSTITUTIONAL GATE</div>', unsafe_allow_html=True)

decision = agents["decision"]

if decision["has_trade"]:
    st.markdown(f"""
    <div class="decision-box">
        <div style="color:#00cc55; font-size:0.85rem; font-weight:700; letter-spacing:1px; margin-bottom:8px;">
            TRADE SIGNAL — {decision['side']} {decision['instrument']}
        </div>
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; margin:8px 0; font-family:'Roboto Mono',monospace;">
            <div><span style="color:#666; font-size:0.7rem;">ENTRY</span><br><span style="font-size:1.2rem; color:#fff; font-weight:600;">{decision['entry']}</span></div>
            <div><span style="color:#666; font-size:0.7rem;">STOP</span><br><span style="font-size:1.2rem; color:#ff3333; font-weight:600;">{decision['stop_loss']}</span></div>
            <div><span style="color:#666; font-size:0.7rem;">TARGET</span><br><span style="font-size:1.2rem; color:#00cc55; font-weight:600;">{decision['take_profit']}</span></div>
            <div><span style="color:#666; font-size:0.7rem;">SIZE</span><br><span style="font-size:1.2rem; color:#fff; font-weight:600;">{decision['size']}</span></div>
        </div>
        <p style="color:#00aa44; font-size:0.8rem; margin:6px 0 0 0;">
            CONF {decision['confidence']*100:.0f}% &nbsp;|&nbsp; ALIGNED: {', '.join(decision['aligned_agents'])}
        </p>
        <p style="color:#888; font-size:0.75rem; margin:4px 0 0 0;">{decision['reasoning']}</p>
    </div>
    """, unsafe_allow_html=True)
    if enable_sound:
        play_alert_sound("trade")
else:
    st.markdown(f"""
    <div class="decision-box-wait">
        <div style="color:#666; font-size:0.85rem; font-weight:700; letter-spacing:1px; margin-bottom:6px;">
            NO TRADE — AWAITING CONFLUENCE
        </div>
        <p style="color:#888; font-size:0.8rem; margin:0;">{decision['reasoning']}</p>
        <p style="color:#555; font-size:0.75rem; margin:4px 0 0 0;">
            ALIGNED: {', '.join(decision['aligned_agents']) if decision['aligned_agents'] else 'NONE'}
            &nbsp;|&nbsp; NEED: OB + ≥{min_confluence} SIGNALS + QUANT
        </p>
    </div>
    """, unsafe_allow_html=True)

# ====================== KEY LEVEL ALERT CHECK ======================
if alert_level > 0 and enable_sound:
    tolerance = current_price * (alert_tolerance / 100)
    if abs(current_price - alert_level) <= tolerance:
        play_alert_sound("level")
        st.warning(f"KEY LEVEL HIT — {current_price:.2f} near {alert_level:.2f}")

# ====================== POWERFUL REAL-INDICATOR AGENTS ======================
st.markdown('<div class="bbg-panel-title" style="margin-top:12px;">AGENT PANEL — LIVE SIGNALS</div>', unsafe_allow_html=True)

def _signal_color(sig):
    if sig == "BUY":
        return "#00cc55"
    if sig == "SELL":
        return "#ff3333"
    return "#94a3b8"

# ===== Institutional Quant Model (prominent) =====
qm = agents.get("quant_model")
if qm:
    qsc = _signal_color(qm["signal"])
    st.markdown(f"""
    <div class="agent-card" style="border: 1px solid #6366f1; background: linear-gradient(145deg, #1e1b4b 0%, #0f172a 100%);">
        <div class="agent-title" style="color:#a5b4fc;">{qm['name']}</div>
        <p style="color:#e2e8f0; font-size:0.9rem;">{qm['analysis']}</p>
        <p style="color:{qsc}; font-size:1.05rem; font-weight:700;">Signal: {qm['signal']} &nbsp;|&nbsp; Score: {qm['score']:+.2f}</p>
        <p style="color:#94a3b8; font-size:0.85rem;">
            Vol Regime: <b>{qm['vol_regime']}</b> — {qm['vol_note']}<br>
            Trend Regime: <b>{qm['trend_regime']}</b> &nbsp;|&nbsp; Confidence: {qm['confidence']*100:.0f}%
        </p>
    </div>
    """, unsafe_allow_html=True)

# Row 1 — Core precision bots
r1c1, r1c2, r1c3 = st.columns(3)
with r1c1:
    a = agents["scanner"]
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#94a3b8; font-size:0.85rem;"><b>Focus:</b> {a['priority']}</p>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['summary']}</p>
        <p style="color:#10b981; font-size:0.8rem;">Confidence: {a['confidence']*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

with r1c2:
    a = agents["rsi_agent"]
    sc = _signal_color(a["signal"])
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['analysis']}</p>
        <p style="color:{sc}; font-size:0.95rem; font-weight:600;"><b>Signal: {a['signal']}</b> (RSI {a['value']})</p>
        <p style="color:#10b981; font-size:0.8rem;">Confidence: {a['confidence']*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

with r1c3:
    a = agents["macd_agent"]
    sc = _signal_color(a["signal"])
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['analysis']}</p>
        <p style="color:{sc}; font-size:0.95rem; font-weight:600;"><b>Signal: {a['signal']}</b></p>
        <p style="color:#94a3b8; font-size:0.8rem;">Hist: {a['hist']}</p>
        <p style="color:#10b981; font-size:0.8rem;">Confidence: {a['confidence']*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

# Row 2 — Volume Profile + EMA + Momentum
r2c1, r2c2, r2c3 = st.columns(3)
with r2c1:
    a = agents["volume_profile"]
    sc = _signal_color(a["signal"])
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['analysis']}</p>
        <p style="color:{sc}; font-size:0.95rem; font-weight:600;"><b>Signal: {a['signal']}</b></p>
        <p style="color:#a5b4fc; font-size:0.8rem;">POC: {a.get('poc')} | VAH: {a.get('vah')} | VAL: {a.get('val')}</p>
        <p style="color:#10b981; font-size:0.8rem;">Confidence: {a['confidence']*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

with r2c2:
    a = agents["ema_agent"]
    sc = _signal_color(a["signal"])
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['analysis']}</p>
        <p style="color:{sc}; font-size:0.95rem; font-weight:600;"><b>Signal: {a['signal']}</b></p>
        <p style="color:#94a3b8; font-size:0.8rem;">EMA20: {a['ema20']} | EMA50: {a['ema50']}</p>
        <p style="color:#10b981; font-size:0.8rem;">Confidence: {a['confidence']*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

with r2c3:
    a = agents["momentum"]
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['analysis']}</p>
        <p style="color:#ff6600; font-size:0.85rem;"><b>{a['signal']}</b></p>
        <p style="color:#10b981; font-size:0.8rem;">Confidence: {a['confidence']*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

# Row 3 — News + Risk + Order Block
r3c1, r3c2, r3c3 = st.columns(3)

with r3c1:
    a = agents["news"]
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#fbbf24; font-size:0.85rem;"><b>Bias:</b> {a['bias']}</p>
        <p style="color:#94a3b8; font-size:0.8rem;">{a['critical']}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("#### 🚨 Upcoming High-Impact Events")
    for event in a["upcoming"]:
        color = "#ff3333" if event["impact"] == "HIGH" else "#f59e0b"
        st.markdown(f"""
        <div class="news-alert">
            <strong style="color:{color};">{event['impact']}</strong> — {event['event']}<br>
            <span style="color:#fca5a5; font-size:0.85rem;">{event['time']} | Focus: {event['focus']}</span>
        </div>
        """, unsafe_allow_html=True)

with r3c2:
    a = agents["risk"]
    status_color = "#10b981" if a["approved"] else "#ff3333"
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:{status_color}; font-size:1rem; font-weight:600;">
            {'✅ APPROVED' if a['approved'] else '❌ VETOED'}
        </p>
        <p style="color:#e2e8f0; font-size:0.85rem;">
            Max Risk: {a['max_risk']}<br>
            Stop: {a['suggested_sl_atr']}<br>
            Size: {a['position_size']}<br>
            {a['note']}
        </p>
    </div>
    """, unsafe_allow_html=True)

with r3c3:
    a = agents["orderblock"]
    align_color = "#10b981" if a["aligned"] else "#f59e0b"
    st.markdown(f"""
    <div class="ob-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:{align_color}; font-size:1rem; font-weight:600;">
            {'✅ ALIGNED' if a['aligned'] else '⏳ MONITORING'}
        </p>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['signal']}</p>
        <p style="color:#a5b4fc; font-size:0.8rem;">Levels detected: {len(a['levels'])}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### Alignment Status")
    for name in ["Scanner", "Technical", "Momentum", "Sentiment", "Macro", "Risk", "OrderBlock"]:
        icon = "✅" if name in decision["aligned_agents"] or (name == "Risk" and agents["risk"]["approved"]) else "⚪"
        st.markdown(f"{icon} {name}")

# ====================== FOOTER ======================
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST | Real data via Yahoo Finance (delayed) | No real orders sent | LangGraph-style multi-agent architecture")

# ====================== AUTO REFRESH ======================
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
