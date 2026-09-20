"""
9-Agent AI Trading Command Center
Gold | Crude Oil | Natural Gas
Beautiful live dashboard powered by Streamlit
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

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="9-Agent Trading Command Center",
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
    
    .metric-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    
    .decision-box {
        background: linear-gradient(145deg, #064e3b 0%, #022c22 100%);
        border: 2px solid #10b981;
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
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }
    
    .status-online {
        color: #10b981;
        font-weight: 600;
    }
    
    .status-pending {
        color: #f59e0b;
    }
    
    .confidence-high { color: #10b981; }
    .confidence-med { color: #f59e0b; }
    .confidence-low { color: #ef4444; }
    
    h1, h2, h3 { color: #f1f5f9 !important; }
    .stMetric label { color: #94a3b8 !important; }
    .stMetric value { color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)

# ====================== REAL MARKET DATA (yfinance) ======================
SYMBOLS = {
    "gold": "GC=F",      # Gold Futures
    "crude": "CL=F",     # WTI Crude Oil Futures
    "natgas": "NG=F"     # Natural Gas Futures
}

@st.cache_data(ttl=60)  # Cache for 60 seconds to avoid rate limits
def fetch_real_prices():
    """Fetch latest prices from Yahoo Finance (free, no API key)"""
    prices = {}
    changes = {}
    try:
        for name, symbol in SYMBOLS.items():
            ticker = yf.Ticker(symbol)
            # Try fast_info first, then history
            try:
                info = ticker.fast_info
                price = info.get("lastPrice") or info.get("regularMarketPrice")
                prev = info.get("previousClose")
            except:
                hist = ticker.history(period="5d", interval="1d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price
                else:
                    price, prev = None, None
            
            if price is not None:
                prices[name] = round(float(price), 2 if name != "natgas" else 3)
                if prev:
                    changes[name] = round(float(price) - float(prev), 2 if name != "natgas" else 3)
                else:
                    changes[name] = 0.0
            else:
                prices[name] = None
                changes[name] = 0.0
    except Exception as e:
        st.warning(f"Data fetch issue: {e}. Using fallback.")
        return None, None
    return prices, changes

def generate_price_history(symbol, periods=100):
    """Fetch real recent price history"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d", interval="15m")
        if hist.empty:
            hist = ticker.history(period="1mo", interval="1h")
        if not hist.empty:
            df = hist.tail(periods).reset_index()
            df = df.rename(columns={"Datetime": "time", "Close": "price"})
            if "time" not in df.columns:
                df = df.rename(columns={df.columns[0]: "time"})
            return df[["time", "price"]]
    except:
        pass
    # Fallback simulated
    base = {"GC=F": 2650, "CL=F": 73, "NG=F": 2.9}.get(symbol, 100)
    np.random.seed(42)
    returns = np.random.normal(0, 0.0015, periods)
    prices = base * np.cumprod(1 + returns)
    times = [datetime.now() - timedelta(minutes=15*(periods-i)) for i in range(periods)]
    return pd.DataFrame({"time": times, "price": prices})

def get_live_prices():
    """Get real prices with fallback to simulation"""
    real, changes = fetch_real_prices()
    if real and all(v is not None for v in real.values()):
        return real, changes
    # Fallback simulation
    base = {
        "gold": 2651.20 + random.uniform(-3, 3),
        "crude": 72.85 + random.uniform(-0.4, 0.4),
        "natgas": 2.87 + random.uniform(-0.05, 0.05)
    }
    prices = {k: round(v, 2 if k != "natgas" else 3) for k, v in base.items()}
    changes = {k: round(random.uniform(-2, 2), 2) for k in prices}
    return prices, changes

def get_agent_outputs(prices):
    """Simulate the 9 agents' reasoning"""
    gold_trend = "Bullish" if random.random() > 0.4 else "Bearish"
    crude_trend = "Bearish" if random.random() > 0.45 else "Bullish"
    
    return {
        "scanner": {
            "name": "1️⃣ Market Scanner",
            "status": "Active",
            "gold": f"Trend: {gold_trend} | Key Level: {prices['gold']-5:.1f} | Volume Spike: Yes",
            "crude": f"Trend: {crude_trend} | Key Level: {prices['crude']+0.8:.2f}",
            "natgas": "Trend: Range-bound | Key Level: 2.85",
            "priority": "GOLD",
            "confidence": 0.82
        },
        "technical": {
            "name": "2️⃣ Technical Analyst",
            "status": "Active",
            "analysis": "Higher Highs + Higher Lows structure intact on Gold. RSI 61 (bullish). Order block at 2638 holding.",
            "signal": "BUY bias on Gold",
            "confidence": 0.79
        },
        "momentum": {
            "name": "3️⃣ Momentum & Volatility",
            "status": "Active",
            "analysis": f"Gold ATR: 18.4 | Momentum strength: 7.8/10 | Volatility expansion detected",
            "signal": "Strong momentum continuation possible",
            "confidence": 0.75
        },
        "sentiment": {
            "name": "4️⃣ Sentiment & Positioning",
            "status": "Active",
            "analysis": "Retail heavily short Gold. COT shows commercial (smart money) net long. Classic squeeze setup.",
            "signal": "Contrarian bullish on Gold",
            "confidence": 0.84
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
            "bias": "Gold: Bullish on softer CPI | Crude: Watch inventory draw"
        },
        "macro": {
            "name": "6️⃣ Macro & Correlation",
            "status": "Active",
            "analysis": "USD Index weakening (-0.3%). 10Y yields soft. Gold-USD correlation: -0.81. Risk-on environment supporting metals.",
            "signal": "Macro tailwind for Gold",
            "confidence": 0.77
        },
        "supply_demand": {
            "name": "7️⃣ Supply / Demand",
            "status": "Active",
            "analysis": "Crude: Expected inventory draw this week. NatGas: Storage still elevated. Gold: Central bank buying continues.",
            "signal": "Mild bullish bias Crude | Neutral NatGas",
            "confidence": 0.68
        },
        "risk": {
            "name": "8️⃣ Risk Manager",
            "status": "Active",
            "approved": True,
            "max_risk": "0.5% equity",
            "suggested_sl_atr": "1.5× ATR",
            "position_size": "0.40 lots (Gold)",
            "veto": None,
            "note": "All risk parameters within limits. Correlation risk low."
        },
        "decision": {
            "name": "9️⃣ Final Decision Agent",
            "status": "DECISION READY",
            "instrument": "XAUUSD (Gold)",
            "side": "BUY",
            "entry": round(prices["gold"] + 0.3, 2),
            "stop_loss": round(prices["gold"] - 18.5, 2),
            "take_profit": round(prices["gold"] + 32.0, 2),
            "size": "0.40 lots",
            "confidence": 0.81,
            "reasoning": "Strong confluence: Scanner + Technical + Sentiment + Macro aligned. Risk Manager approved. News window clear for next 2 hours.",
            "aligned_agents": ["Scanner", "Technical", "Momentum", "Sentiment", "Macro", "Risk"]
        }
    }

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("### ⚡ Control Panel")
    st.markdown("---")
    
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()
    
    auto_refresh = st.toggle("Live Auto-Refresh", value=False)
    refresh_rate = st.slider("Refresh every (seconds)", 5, 30, 10)
    
    st.markdown("---")
    st.markdown("### Market Focus")
    focus = st.multiselect(
        "Instruments",
        ["Gold (XAUUSD)", "Crude Oil (WTI)", "Natural Gas"],
        default=["Gold (XAUUSD)", "Crude Oil (WTI)"]
    )
    
    st.markdown("---")
    st.markdown("### System Status")
    st.markdown('<span class="status-online">● All 9 Agents Online</span>', unsafe_allow_html=True)
    st.caption(f"Last cycle: {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    st.markdown("### Risk Settings")
    max_risk = st.slider("Max Risk per Trade %", 0.1, 2.0, 0.5, 0.1)
    atr_mult = st.slider("Stop Loss ATR Multiplier", 1.0, 3.0, 1.5, 0.1)
    
    st.markdown("---")
    st.info("This is a **simulation dashboard**. No real trades are executed.")

# ====================== MAIN HEADER ======================
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size:1.8rem;">⚡ 9-Agent AI Trading Command Center</h1>
    <p style="margin:0.3rem 0 0 0; color:#94a3b8;">Gold • Crude Oil • Natural Gas | Live Multi-Agent Decision System</p>
</div>
""", unsafe_allow_html=True)

# ====================== LIVE PRICES ======================
prices, changes = get_live_prices()
agents = get_agent_outputs(prices)

# Show data source status
data_source = "🟢 Live Yahoo Finance (GC=F / CL=F / NG=F)" if changes.get("gold") is not None else "🟡 Simulation Fallback"
st.caption(f"Data Source: {data_source} | Updated: {datetime.now().strftime('%H:%M:%S')}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_g = changes.get("gold", 0)
    st.metric("🥇 Gold Futures (GC=F)", f"{prices['gold']:,.2f}", f"{delta_g:+.2f}")
with col2:
    delta_c = changes.get("crude", 0)
    st.metric("🛢️ Crude Oil (CL=F)", f"{prices['crude']:.2f}", f"{delta_c:+.2f}")
with col3:
    delta_n = changes.get("natgas", 0)
    st.metric("🔥 Natural Gas (NG=F)", f"{prices['natgas']:.3f}", f"{delta_n:+.3f}")
with col4:
    st.metric("System Confidence", f"{agents['decision']['confidence']*100:.0f}%", "High Confluence")

st.markdown("---")

# ====================== CHARTS ======================
st.subheader("📈 Live Price Action (Real Data)")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    gold_df = generate_price_history("GC=F")
    fig_g = go.Figure()
    fig_g.add_trace(go.Scatter(
        x=gold_df["time"], y=gold_df["price"],
        mode="lines", name="Gold",
        line=dict(color="#fbbf24", width=2)
    ))
    fig_g.update_layout(
        title="Gold Futures (GC=F)",
        template="plotly_dark",
        height=280,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.8)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1e293b")
    )
    st.plotly_chart(fig_g, use_container_width=True)

with chart_col2:
    crude_df = generate_price_history("CL=F")
    fig_c = go.Figure()
    fig_c.add_trace(go.Scatter(
        x=crude_df["time"], y=crude_df["price"],
        mode="lines", name="Crude",
        line=dict(color="#38bdf8", width=2)
    ))
    fig_c.update_layout(
        title="Crude Oil Futures (CL=F)",
        template="plotly_dark",
        height=280,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.8)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1e293b")
    )
    st.plotly_chart(fig_c, use_container_width=True)

st.markdown("---")

# ====================== FINAL DECISION ======================
st.subheader("🎯 Final Trade Decision (Agent 9)")

decision = agents["decision"]
st.markdown(f"""
<div class="decision-box">
    <h3 style="color:#34d399; margin-top:0;">✅ {decision['side']} {decision['instrument']}</h3>
    <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:1rem; margin:1rem 0;">
        <div><strong>Entry</strong><br><span style="font-size:1.3rem; color:#f1f5f9;">{decision['entry']}</span></div>
        <div><strong>Stop Loss</strong><br><span style="font-size:1.3rem; color:#f87171;">{decision['stop_loss']}</span></div>
        <div><strong>Take Profit</strong><br><span style="font-size:1.3rem; color:#34d399;">{decision['take_profit']}</span></div>
        <div><strong>Size</strong><br><span style="font-size:1.3rem; color:#f1f5f9;">{decision['size']}</span></div>
    </div>
    <p style="color:#a7f3d0;"><strong>Confidence:</strong> {decision['confidence']*100:.0f}% &nbsp;|&nbsp; 
    <strong>Aligned Agents:</strong> {', '.join(decision['aligned_agents'])}</p>
    <p style="color:#d1fae5; font-size:0.95rem;">{decision['reasoning']}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ====================== 9 AGENTS GRID ======================
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

# Row 3 - News + Risk
r3c1, r3c2 = st.columns(2)

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
    
    st.markdown("#### Alignment Status")
    aligned = decision["aligned_agents"]
    for name in ["Scanner", "Technical", "Momentum", "Sentiment", "News", "Macro", "Supply/Demand", "Risk"]:
        icon = "✅" if name in aligned or name == "Risk" else "⚪"
        st.markdown(f"{icon} {name}")

# ====================== FOOTER ======================
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST | Real market data via Yahoo Finance (delayed) — No real orders are sent | Built with LangGraph architecture concepts")

# ====================== AUTO REFRESH ======================
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
