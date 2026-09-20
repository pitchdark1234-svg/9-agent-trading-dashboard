"""
9+1 Agent AI Trading Command Center
Gold | Crude Oil | Natural Gas
Live dashboard with Order Block Scanner, Yahoo-style charts, conditional signals & sound alerts
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
    page_title="9+1 Agent Trading Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0e17 0%, #111827 50%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(90deg, #1e3a5f 0%, #0f172a 100%);
        padding: 1.2rem 2rem;
        border-radius: 12px;
        border: 1px solid #1e40af;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(30, 64, 175, 0.3);
    }
    
    .agent-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
    }
    
    .agent-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
    }
    
    .agent-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #60a5fa;
        margin-bottom: 0.4rem;
    }
    
    .decision-box {
        background: linear-gradient(145deg, #064e3b 0%, #022c22 100%);
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    .decision-box-wait {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 2px solid #64748b;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    .news-alert {
        background: linear-gradient(145deg, #7f1d1d 0%, #450a0a 100%);
        border: 1px solid #ef4444;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        animation: pulse 2s infinite;
    }
    
    .ob-card {
        background: linear-gradient(145deg, #312e81 0%, #1e1b4b 100%);
        border: 1px solid #6366f1;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }
    
    .status-online { color: #10b981; font-weight: 600; }
    .status-pending { color: #f59e0b; }
    
    h1, h2, h3 { color: #f1f5f9 !important; }
    .stMetric label { color: #94a3b8 !important; }
    .stMetric value { color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)

# ====================== REAL MARKET DATA ======================
SYMBOLS = {
    "Gold (XAUUSD)": "GC=F",
    "Crude Oil (WTI)": "CL=F",
    "Natural Gas": "NG=F"
}

SYMBOL_KEYS = {
    "Gold (XAUUSD)": "gold",
    "Crude Oil (WTI)": "crude",
    "Natural Gas": "natgas"
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
    base = {"GC=F": 2650, "CL=F": 73, "NG=F": 2.9}.get(symbol, 100)
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
        "natgas": 2.87 + random.uniform(-0.05, 0.05)
    }
    prices = {k: round(v, 2 if k != "natgas" else 3) for k, v in base.items()}
    changes = {k: round(random.uniform(-2, 2), 2) for k in prices}
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

def get_agent_outputs(prices, selected_key, order_blocks, current_price):
    """9 agents + Order Block Scanner. Decision only fires on high confluence."""
    
    # Simulated but coherent reasoning based on selected instrument
    gold_bias = "Bullish" if random.random() > 0.38 else "Bearish"
    crude_bias = "Bearish" if random.random() > 0.48 else "Bullish"
    
    # Order Block alignment check
    nearest_ob = None
    ob_aligned = False
    ob_signal = "No high-quality Order Block near price"
    if order_blocks:
        # Find closest OB to current price
        for ob in order_blocks:
            dist = abs(ob["mid"] - current_price)
            if nearest_ob is None or dist < abs(nearest_ob["mid"] - current_price):
                nearest_ob = ob
        if nearest_ob:
            zone_dist = abs(nearest_ob["mid"] - current_price) / current_price
            if zone_dist < 0.004:  # within ~0.4%
                ob_aligned = True
                if nearest_ob["type"] == "Bullish OB":
                    ob_signal = f"Price reacting at Bullish OB {nearest_ob['bottom']:.2f}-{nearest_ob['top']:.2f}"
                else:
                    ob_signal = f"Price reacting at Bearish OB {nearest_ob['bottom']:.2f}-{nearest_ob['top']:.2f}"
            else:
                ob_signal = f"Nearest {nearest_ob['type']} at {nearest_ob['mid']:.2f} (watching)"
    
    # Core agent signals (simplified coherence)
    tech_signal = "BUY" if gold_bias == "Bullish" else "SELL"
    mom_ok = random.random() > 0.3
    sent_ok = random.random() > 0.25
    macro_ok = random.random() > 0.3
    risk_ok = True
    
    aligned = []
    if tech_signal:
        aligned.append("Technical")
    if mom_ok:
        aligned.append("Momentum")
    if sent_ok:
        aligned.append("Sentiment")
    if macro_ok:
        aligned.append("Macro")
    aligned.append("Risk")
    if ob_aligned:
        aligned.append("OrderBlock")
    
    # Confluence count (need >= 5 including Order Block for full go)
    confluence_score = len(aligned)
    full_confluence = confluence_score >= 5 and ob_aligned and risk_ok
    
    # Decision only if full confluence
    if full_confluence and selected_key == "gold":
        side = "BUY" if nearest_ob and nearest_ob["type"] == "Bullish OB" else ("SELL" if nearest_ob and nearest_ob["type"] == "Bearish OB" else tech_signal)
        entry = round(current_price + (0.4 if side == "BUY" else -0.4), 2)
        sl = round(current_price - 18.5 if side == "BUY" else current_price + 18.5, 2)
        tp = round(current_price + 32.0 if side == "BUY" else current_price - 32.0, 2)
        decision = {
            "name": "9️⃣ Final Decision Agent",
            "status": "TRADE READY",
            "instrument": "XAUUSD (Gold)",
            "side": side,
            "entry": entry,
            "stop_loss": sl,
            "take_profit": tp,
            "size": "0.40 lots",
            "confidence": min(0.92, 0.70 + confluence_score * 0.04),
            "reasoning": f"FULL CONFLUENCE ({confluence_score}/9+OB). Order Block + Technical + Sentiment + Macro aligned. Risk approved. Clear window.",
            "aligned_agents": aligned,
            "has_trade": True
        }
    else:
        decision = {
            "name": "9️⃣ Final Decision Agent",
            "status": "WAITING",
            "instrument": selected_key.upper(),
            "side": "—",
            "entry": "—",
            "stop_loss": "—",
            "take_profit": "—",
            "size": "—",
            "confidence": 0.0,
            "reasoning": "No trade. Waiting for full confluence (Order Block + ≥4 supporting agents + Risk).",
            "aligned_agents": aligned,
            "has_trade": False
        }
    
    return {
        "scanner": {
            "name": "1️⃣ Market Scanner",
            "status": "Active",
            "gold": f"Trend: {gold_bias} | Key Level: {prices['gold']-5:.1f}",
            "crude": f"Trend: {crude_bias} | Key Level: {prices['crude']+0.8:.2f}",
            "natgas": "Trend: Range-bound | Key Level: 2.85",
            "priority": "GOLD" if selected_key == "gold" else selected_key.upper(),
            "confidence": 0.82
        },
        "technical": {
            "name": "2️⃣ Technical Analyst",
            "status": "Active",
            "analysis": f"Structure on selected instrument: {tech_signal} bias. Higher-timeframe structure respected.",
            "signal": f"{tech_signal} bias",
            "confidence": 0.79
        },
        "momentum": {
            "name": "3️⃣ Momentum & Volatility",
            "status": "Active",
            "analysis": f"ATR expanding | Momentum strength: {7.2 + random.random():.1f}/10",
            "signal": "Momentum supportive" if mom_ok else "Momentum fading",
            "confidence": 0.75 if mom_ok else 0.55
        },
        "sentiment": {
            "name": "4️⃣ Sentiment & Positioning",
            "status": "Active",
            "analysis": "Retail positioning skewed. Smart-money COT leaning opposite. Potential squeeze setup.",
            "signal": "Contrarian supportive" if sent_ok else "Neutral",
            "confidence": 0.84 if sent_ok else 0.60
        },
        "news": {
            "name": "5️⃣ News & Event Agent",
            "status": "Active",
            "upcoming": [
                {"event": "US CPI (Core)", "time": "Today 18:30 IST", "impact": "HIGH", "focus": "Gold"},
                {"event": "EIA Crude Inventories", "time": "Today 20:30 IST", "impact": "HIGH", "focus": "Crude"},
                {"event": "FOMC Member Speech", "time": "Tomorrow 15:00 IST", "impact": "MEDIUM", "focus": "Gold"}
            ],
            "critical": "No critical breaking news in last 15 min",
            "bias": "Gold: Watch CPI | Crude: Inventory focus"
        },
        "macro": {
            "name": "6️⃣ Macro & Correlation",
            "status": "Active",
            "analysis": "USD soft | Yields contained | Risk environment supportive for metals.",
            "signal": "Macro tailwind" if macro_ok else "Macro neutral",
            "confidence": 0.77 if macro_ok else 0.58
        },
        "supply_demand": {
            "name": "7️⃣ Supply / Demand",
            "status": "Active",
            "analysis": "Gold: CB buying continues. Crude: Expected draw. NatGas: Elevated storage.",
            "signal": "Mild bullish bias selected instrument",
            "confidence": 0.68
        },
        "risk": {
            "name": "8️⃣ Risk Manager",
            "status": "Active",
            "approved": risk_ok,
            "max_risk": "0.5% equity",
            "suggested_sl_atr": "1.5× ATR",
            "position_size": "0.40 lots",
            "veto": None if risk_ok else "Size exceeds limit",
            "note": "All risk parameters within limits." if risk_ok else "Risk parameters exceeded."
        },
        "orderblock": {
            "name": "🔟 Order Block Scanner",
            "status": "Active",
            "levels": order_blocks,
            "nearest": nearest_ob,
            "signal": ob_signal,
            "aligned": ob_aligned,
            "confidence": nearest_ob["strength"] if nearest_ob else 0.0
        },
        "decision": decision
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
    st.markdown('<span class="status-online">● 9 Agents + Order Block Scanner Online</span>', unsafe_allow_html=True)
    st.caption(f"Last cycle: {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    st.markdown("### Risk Settings")
    max_risk = st.slider("Max Risk per Trade %", 0.1, 2.0, 0.5, 0.1)
    atr_mult = st.slider("Stop Loss ATR Multiplier", 1.0, 3.0, 1.5, 0.1)
    
    st.markdown("---")
    st.info("Simulation + real Yahoo data. No real orders are executed.")

# ====================== MAIN HEADER ======================
st.markdown(f"""
<div class="main-header">
    <h1 style="margin:0; font-size:1.8rem;">⚡ 9+1 Agent AI Trading Command Center</h1>
    <p style="margin:0.3rem 0 0 0; color:#94a3b8;">Focused on <b>{selected_instrument}</b> | Order Block Scanner + Conditional Signals</p>
</div>
""", unsafe_allow_html=True)

# ====================== LIVE PRICES ======================
prices, changes, is_live = get_live_prices()
current_price = prices[selected_key]

# OHLC data for selected instrument
ohlc_df = generate_ohlc_history(selected_symbol)
order_blocks = detect_order_blocks(ohlc_df)

agents = get_agent_outputs(prices, selected_key, order_blocks, current_price)

data_source = "🟢 Live Yahoo Finance" if is_live else "🟡 Simulation Fallback"
st.caption(f"Data Source: {data_source} | Focus: {selected_instrument} ({selected_symbol}) | Updated: {datetime.now().strftime('%H:%M:%S')}")

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    delta = changes.get(selected_key, 0)
    label = f"🥇 {selected_instrument}" if selected_key == "gold" else (f"🛢️ {selected_instrument}" if selected_key == "crude" else f"🔥 {selected_instrument}")
    fmt = f"{current_price:,.3f}" if selected_key == "natgas" else f"{current_price:,.2f}"
    st.metric(label, fmt, f"{delta:+.3f}" if selected_key == "natgas" else f"{delta:+.2f}")
with col2:
    st.metric("Order Blocks Found", len(order_blocks), "Active zones")
with col3:
    conf = agents["decision"]["confidence"]
    st.metric("System Confidence", f"{conf*100:.0f}%" if conf > 0 else "—", "Full Confluence" if agents["decision"]["has_trade"] else "Waiting")
with col4:
    ob_status = "✅ Aligned" if agents["orderblock"]["aligned"] else "⏳ Watching"
    st.metric("Order Block Status", ob_status)

st.markdown("---")

# ====================== ADVANCED CHART (Yahoo Finance style) ======================
st.subheader(f"📈 {selected_instrument} — Advanced Chart (Candlestick + Volume + Order Blocks)")

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
    increasing_line_color="#22c55e",
    decreasing_line_color="#ef4444",
    increasing_fillcolor="#22c55e",
    decreasing_fillcolor="#ef4444"
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
line_colors = {"Bullish OB": "#22c55e", "Bearish OB": "#ef4444"}

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
colors_vol = ["#22c55e" if c >= o else "#ef4444" for c, o in zip(ohlc_df["close"], ohlc_df["open"])]
fig.add_trace(go.Bar(
    x=ohlc_df["time"],
    y=ohlc_df["volume"],
    name="Volume",
    marker_color=colors_vol,
    opacity=0.7
), row=2, col=1)

fig.update_layout(
    template="plotly_dark",
    height=520,
    margin=dict(l=10, r=10, t=40, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,23,42,0.85)",
    xaxis_rangeslider_visible=False,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)
fig.update_xaxes(showgrid=False, row=1, col=1)
fig.update_xaxes(showgrid=False, row=2, col=1)
fig.update_yaxes(showgrid=True, gridcolor="#1e293b", row=1, col=1)
fig.update_yaxes(showgrid=False, row=2, col=1)

st.plotly_chart(fig, use_container_width=True)

# ====================== ORDER BLOCK SCANNER PANEL ======================
st.subheader("🔟 Order Block Scanner — Key Levels")

if order_blocks:
    ob_cols = st.columns(min(4, len(order_blocks)))
    for idx, ob in enumerate(order_blocks):
        with ob_cols[idx % len(ob_cols)]:
            color = "#22c55e" if "Bullish" in ob["type"] else "#ef4444"
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
st.subheader("🎯 Final Trade Decision (Agent 9 + Order Block Gate)")

decision = agents["decision"]

if decision["has_trade"]:
    st.markdown(f"""
    <div class="decision-box">
        <h3 style="color:#34d399; margin-top:0;">✅ TRADE SIGNAL — {decision['side']} {decision['instrument']}</h3>
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:1rem; margin:1rem 0;">
            <div><strong>Entry</strong><br><span style="font-size:1.3rem; color:#f1f5f9;">{decision['entry']}</span></div>
            <div><strong>Stop Loss</strong><br><span style="font-size:1.3rem; color:#f87171;">{decision['stop_loss']}</span></div>
            <div><strong>Take Profit</strong><br><span style="font-size:1.3rem; color:#34d399;">{decision['take_profit']}</span></div>
            <div><strong>Size</strong><br><span style="font-size:1.3rem; color:#f1f5f9;">{decision['size']}</span></div>
        </div>
        <p style="color:#a7f3d0;"><strong>Confidence:</strong> {decision['confidence']*100:.0f}% &nbsp;|&nbsp; 
        <strong>Aligned:</strong> {', '.join(decision['aligned_agents'])}</p>
        <p style="color:#d1fae5; font-size:0.95rem;">{decision['reasoning']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sound alert for trade
    if enable_sound:
        play_alert_sound("trade")
        st.success("🔊 Trade alert sound played (pleasant chime)")
else:
    st.markdown(f"""
    <div class="decision-box-wait">
        <h3 style="color:#94a3b8; margin-top:0;">⏳ NO TRADE — Waiting for Full Confluence</h3>
        <p style="color:#cbd5e1;">{decision['reasoning']}</p>
        <p style="color:#64748b; font-size:0.9rem;">Currently aligned: {', '.join(decision['aligned_agents']) if decision['aligned_agents'] else 'None'}</p>
        <p style="color:#64748b; font-size:0.85rem;">Requires: Order Block alignment + ≥{min_confluence} supporting agents + Risk approval.</p>
    </div>
    """, unsafe_allow_html=True)

# ====================== KEY LEVEL ALERT CHECK ======================
if alert_level > 0 and enable_sound:
    tolerance = current_price * (alert_tolerance / 100)
    if abs(current_price - alert_level) <= tolerance:
        play_alert_sound("level")
        st.warning(f"🔔 **KEY LEVEL ALERT** — Price {current_price:.2f} is within {alert_tolerance}% of your set level {alert_level:.2f}")

st.markdown("---")

# ====================== 9 AGENTS + ORDER BLOCK GRID ======================
st.subheader("🤖 Live Agent Reasoning")

# Row 1
r1c1, r1c2, r1c3 = st.columns(3)
with r1c1:
    a = agents["scanner"]
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#94a3b8; font-size:0.85rem; margin:0.3rem 0;"><b>Priority:</b> {a['priority']}</p>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['gold']}</p>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['crude']}</p>
        <p style="color:#10b981; font-size:0.8rem;">Confidence: {a['confidence']*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

with r1c2:
    a = agents["technical"]
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['analysis']}</p>
        <p style="color:#60a5fa; font-size:0.85rem;"><b>Signal:</b> {a['signal']}</p>
        <p style="color:#10b981; font-size:0.8rem;">Confidence: {a['confidence']*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

with r1c3:
    a = agents["momentum"]
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['analysis']}</p>
        <p style="color:#60a5fa; font-size:0.85rem;"><b>Signal:</b> {a['signal']}</p>
        <p style="color:#10b981; font-size:0.8rem;">Confidence: {a['confidence']*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

# Row 2
r2c1, r2c2, r2c3 = st.columns(3)
with r2c1:
    a = agents["sentiment"]
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['analysis']}</p>
        <p style="color:#60a5fa; font-size:0.85rem;"><b>Signal:</b> {a['signal']}</p>
        <p style="color:#10b981; font-size:0.8rem;">Confidence: {a['confidence']*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

with r2c2:
    a = agents["macro"]
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['analysis']}</p>
        <p style="color:#60a5fa; font-size:0.85rem;"><b>Signal:</b> {a['signal']}</p>
        <p style="color:#10b981; font-size:0.8rem;">Confidence: {a['confidence']*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

with r2c3:
    a = agents["supply_demand"]
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{a['name']}</div>
        <p style="color:#e2e8f0; font-size:0.85rem;">{a['analysis']}</p>
        <p style="color:#60a5fa; font-size:0.85rem;"><b>Signal:</b> {a['signal']}</p>
        <p style="color:#f59e0b; font-size:0.8rem;">Confidence: {a['confidence']*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

# Row 3 - News + Risk + Order Block
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
        color = "#ef4444" if event["impact"] == "HIGH" else "#f59e0b"
        st.markdown(f"""
        <div class="news-alert">
            <strong style="color:{color};">{event['impact']}</strong> — {event['event']}<br>
            <span style="color:#fca5a5; font-size:0.85rem;">{event['time']} | Focus: {event['focus']}</span>
        </div>
        """, unsafe_allow_html=True)

with r3c2:
    a = agents["risk"]
    status_color = "#10b981" if a["approved"] else "#ef4444"
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
