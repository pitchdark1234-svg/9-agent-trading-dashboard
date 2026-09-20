"""
Deep Profile Terminal — Deepcharts-style Volume Profile
POC · Value Area · HVN · LVN · Absorption · VWAP
Gold | Crude | NatGas | Bitcoin
"""

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

st.set_page_config(
    page_title="Deep Profile Terminal",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== DEEPCHARTS-STYLE CSS ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;600;700&display=swap');
.stApp { background: #0b0e11 !important; font-family: 'Roboto Mono', monospace !important; color: #d1d4dc !important; }
.main .block-container { padding-top: 0.5rem !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { background: #131722 !important; border-right: 1px solid #2a2e39 !important; }
h1, h2, h3 { color: #f0b90b !important; font-family: 'Roboto Mono', monospace !important; font-size: 0.95rem !important; }
div[data-testid="stMetric"] { background: #131722 !important; border: 1px solid #2a2e39 !important; border-radius: 2px !important; padding: 6px 10px !important; }
div[data-testid="stMetric"] label { color: #787b86 !important; font-size: 0.62rem !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #d1d4dc !important; font-family: 'Roboto Mono', monospace !important; font-size: 1.05rem !important; }
.stButton > button { background: #1e222d !important; color: #f0b90b !important; border: 1px solid #f0b90b !important; border-radius: 2px !important; font-family: 'Roboto Mono', monospace !important; font-size: 0.75rem !important; text-transform: uppercase !important; }
.stButton > button:hover { background: #f0b90b !important; color: #0b0e11 !important; }
.hdr { background: #131722; border-bottom: 1px solid #f0b90b; padding: 8px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
.hdr-title { color: #f0b90b; font-weight: 700; letter-spacing: 2px; font-size: 0.95rem; }
.hdr-sub { color: #787b86; font-size: 0.7rem; }
.ticker { background: #131722; border: 1px solid #2a2e39; padding: 6px 12px; margin-bottom: 8px; font-size: 0.78rem; color: #787b86; }
.panel { background: #131722; border: 1px solid #2a2e39; padding: 10px 12px; margin-bottom: 8px; border-radius: 2px; }
.panel-t { color: #f0b90b; font-size: 0.68rem; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; border-bottom: 1px solid #2a2e39; padding-bottom: 4px; margin-bottom: 8px; }
.row { display: flex; justify-content: space-between; padding: 3px 0; border-bottom: 1px solid #1a1e28; font-size: 0.76rem; }
.poc { color: #e91e8c; font-weight: 700; }
.vah { color: #26a69a; }
.val { color: #ef5350; }
.hvn { color: #42a5f5; }
.lvn { color: #ab47bc; }
.bull { color: #26a69a; }
.bear { color: #ef5350; }
.amber { color: #f0b90b; }
.abs-buy { color: #26a69a; }
.abs-sell { color: #ef5350; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ====================== SYMBOLS ======================
INSTRUMENTS = {
    "Gold (XAUUSD)": {"tv": "OANDA:XAUUSD", "yf": "GC=F", "dec": 2},
    "Crude Oil (WTI)": {"tv": "NYMEX:CL1!", "yf": "CL=F", "dec": 2},
    "Natural Gas": {"tv": "NYMEX:NG1!", "yf": "NG=F", "dec": 3},
    "Bitcoin (BTC)": {"tv": "BINANCE:BTCUSDT", "yf": "BTC-USD", "dec": 2},
}

# ====================== DATA ======================
@st.cache_data(ttl=60)
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
        df = df.rename(columns={c0: "time", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
        df = df[["time", "open", "high", "low", "close", "volume"]].dropna()
        return df.tail(250).reset_index(drop=True)
    except Exception:
        return None

@st.cache_data(ttl=45)
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

# ====================== VOLUME PROFILE ENGINE ======================
def build_volume_profile(df, bins=48, va_pct=0.70):
    """
    Deepcharts-style Volume Profile:
    - POC, VAH, VAL
    - Volume histogram at each price bin
    - Approximate delta from candle direction
    """
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
        # distribute volume across the bar's range (approximation)
        lo, hi = float(row["low"]), float(row["high"])
        v = float(row["volume"])
        if hi <= lo:
            idx = np.clip(np.searchsorted(edges, (lo + hi) / 2, side="right") - 1, 0, bins - 1)
            vol[idx] += v
            if row["close"] >= row["open"]:
                buy_vol[idx] += v
            else:
                sell_vol[idx] += v
            continue
        # proportional allocation across bins the bar spans
        i0 = np.clip(np.searchsorted(edges, lo, side="right") - 1, 0, bins - 1)
        i1 = np.clip(np.searchsorted(edges, hi, side="right") - 1, 0, bins - 1)
        n = max(1, i1 - i0 + 1)
        share = v / n
        is_buy = row["close"] >= row["open"]
        for i in range(i0, i1 + 1):
            vol[i] += share
            if is_buy:
                buy_vol[i] += share
            else:
                sell_vol[i] += share

    total = vol.sum()
    if total <= 0:
        return None

    poc_idx = int(np.argmax(vol))
    poc = float(centers[poc_idx])

    # Value Area: expand from POC until va_pct of volume
    target = total * va_pct
    left = right = poc_idx
    covered = vol[poc_idx]
    while covered < target and (left > 0 or right < bins - 1):
        left_vol = vol[left - 1] if left > 0 else -1
        right_vol = vol[right + 1] if right < bins - 1 else -1
        if right_vol >= left_vol and right < bins - 1:
            right += 1
            covered += vol[right]
        elif left > 0:
            left -= 1
            covered += vol[left]
        else:
            right += 1
            covered += vol[right]

    vah = float(edges[right + 1])
    val = float(edges[left])
    delta = buy_vol - sell_vol

    return {
        "centers": centers,
        "edges": edges,
        "volume": vol,
        "buy_vol": buy_vol,
        "sell_vol": sell_vol,
        "delta": delta,
        "poc": poc,
        "poc_idx": poc_idx,
        "vah": vah,
        "val": val,
        "total": total,
        "price_min": price_min,
        "price_max": price_max,
    }

def detect_hvn_lvn(profile, sensitivity=0.55):
    """
    Peaks = HVN, Valleys = LVN (Deepcharts Peak/Valley style).
    sensitivity: higher = fewer nodes (stricter).
    """
    if profile is None:
        return [], []
    vol = profile["volume"]
    centers = profile["centers"]
    if vol.max() <= 0:
        return [], []

    mean_v = vol.mean()
    std_v = vol.std() + 1e-12
    # HVN: local peaks above mean + sensitivity * std
    thr_h = mean_v + sensitivity * std_v
    thr_l = mean_v - sensitivity * std_v * 0.5
    hvn, lvn = [], []

    for i in range(1, len(vol) - 1):
        if vol[i] >= vol[i - 1] and vol[i] >= vol[i + 1] and vol[i] >= thr_h:
            hvn.append({
                "price": float(centers[i]),
                "volume": float(vol[i]),
                "pct": float(vol[i] / profile["total"] * 100),
            })
        if vol[i] <= vol[i - 1] and vol[i] <= vol[i + 1] and vol[i] <= max(thr_l, 0):
            lvn.append({
                "price": float(centers[i]),
                "volume": float(vol[i]),
                "pct": float(vol[i] / profile["total"] * 100),
            })

    # keep strongest HVNs / thinnest LVNs
    hvn = sorted(hvn, key=lambda x: x["volume"], reverse=True)[:8]
    lvn = sorted(lvn, key=lambda x: x["volume"])[:6]
    return hvn, lvn

def detect_absorption(df, min_vol_mult=1.8, max_body_pct=0.35):
    """
    Approximate Absorption (Deepcharts style without full tick data):
    - High volume relative to average
    - Small body vs range (price absorbed / rejected)
    - Close rejects the extreme (wick absorption)
    Bid absorption ≈ sellers absorb buys → long upper wick / close weak after high vol
    Ask absorption ≈ buyers absorb sells → long lower wick / close strong after high vol
    """
    if df is None or len(df) < 20:
        return []
    d = df.copy().reset_index(drop=True)
    d["range"] = (d["high"] - d["low"]).replace(0, np.nan)
    d["body"] = (d["close"] - d["open"]).abs()
    d["body_pct"] = d["body"] / d["range"]
    d["upper_wick"] = d["high"] - d[["open", "close"]].max(axis=1)
    d["lower_wick"] = d[["open", "close"]].min(axis=1) - d["low"]
    avg_vol = d["volume"].rolling(20, min_periods=5).mean()

    events = []
    for i in range(len(d)):
        row = d.loc[i]
        av = avg_vol.iloc[i] if not pd.isna(avg_vol.iloc[i]) else row["volume"]
        if av <= 0 or pd.isna(row["range"]) or row["range"] <= 0:
            continue
        if row["volume"] < av * min_vol_mult:
            continue
        if row["body_pct"] > max_body_pct:
            continue

        # Ask absorption (buyers absorb selling) — long lower wick, closes strong
        if row["lower_wick"] > row["body"] * 1.2 and row["close"] >= row["open"]:
            events.append({
                "type": "ASK ABSORPTION",
                "side": "BUY",
                "price": float(row["low"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "volume": float(row["volume"]),
                "time": row["time"],
                "note": "Buyers absorbed sell pressure",
            })
        # Bid absorption (sellers absorb buying) — long upper wick, closes weak
        elif row["upper_wick"] > row["body"] * 1.2 and row["close"] <= row["open"]:
            events.append({
                "type": "BID ABSORPTION",
                "side": "SELL",
                "price": float(row["high"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "volume": float(row["volume"]),
                "time": row["time"],
                "note": "Sellers absorbed buy pressure",
            })

    return events[-12:]

def compute_vwap(df):
    if df is None or len(df) < 2:
        return None
    tp = (df["high"] + df["low"] + df["close"]) / 3
    cum_v = df["volume"].cumsum().replace(0, np.nan)
    vwap = (tp * df["volume"]).cumsum() / cum_v
    return float(vwap.iloc[-1]) if not pd.isna(vwap.iloc[-1]) else None

# ====================== SIDEBAR SETTINGS ======================
with st.sidebar:
    st.markdown("### DEEP PROFILE")
    st.caption("Deepcharts-style settings")
    st.markdown("---")

    if st.button("REFRESH", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    auto = st.toggle("Auto refresh", value=False)
    rate = st.slider("Refresh sec", 20, 120, 45)

    st.markdown("---")
    st.markdown("### INSTRUMENT")
    selected = st.selectbox("Market", list(INSTRUMENTS.keys()), index=0)
    inst = INSTRUMENTS[selected]
    yf_sym = inst["yf"]
    tv_sym = inst["tv"]
    dec = inst["dec"]

    st.markdown("---")
    st.markdown("### PROFILE SETTINGS")
    profile_bars = st.slider("Lookback bars", 40, 200, 100, 10)
    n_bins = st.slider("Profile bins", 24, 80, 48, 4)
    va_pct = st.slider("Value Area %", 50, 90, 70, 5) / 100.0
    hvn_sens = st.slider("HVN / LVN sensitivity", 0.2, 1.5, 0.55, 0.05)

    st.markdown("---")
    st.markdown("### DISPLAY")
    show_vp = st.toggle("Volume Profile histogram", value=True)
    show_poc = st.toggle("POC line", value=True)
    show_va = st.toggle("Value Area (VAH/VAL)", value=True)
    show_hvn = st.toggle("HVN peaks", value=True)
    show_lvn = st.toggle("LVN valleys", value=True)
    show_vwap = st.toggle("VWAP", value=True)
    show_abs = st.toggle("Absorption markers", value=True)
    show_delta = st.toggle("Delta coloring on profile", value=True)

    st.markdown("---")
    st.markdown("### ABSORPTION FILTER")
    abs_vol_mult = st.slider("Min vol × average", 1.2, 3.0, 1.8, 0.1)
    abs_body = st.slider("Max body / range", 0.15, 0.50, 0.35, 0.05)

    st.markdown("---")
    st.markdown("### CHART SOURCE")
    chart_mode = st.radio("Primary chart", ["Deep Profile (Plotly)", "TradingView embed"], index=0)
    tv_tf = st.selectbox("TV interval", ["5", "15", "30", "60"], index=1)

    st.markdown("---")
    st.caption("Approx. profile from Yahoo OHLC volume (not tick data).")
    st.caption("No real orders sent.")

# ====================== DATA + ANALYSIS ======================
ohlc_full = fetch_ohlc(yf_sym)
if ohlc_full is not None:
    ohlc = ohlc_full.tail(profile_bars).reset_index(drop=True)
else:
    ohlc = None

last_px, prev_px = fetch_last(yf_sym)
if last_px is None and ohlc is not None and len(ohlc):
    last_px = float(ohlc["close"].iloc[-1])
    prev_px = float(ohlc["close"].iloc[-2]) if len(ohlc) > 1 else last_px
if last_px is None:
    last_px, prev_px = 0.0, 0.0

delta_px = last_px - (prev_px or last_px)
delta_pct = (delta_px / last_px * 100) if last_px else 0

profile = build_volume_profile(ohlc, bins=n_bins, va_pct=va_pct)
hvn_list, lvn_list = detect_hvn_lvn(profile, sensitivity=hvn_sens) if profile else ([], [])
absorptions = detect_absorption(ohlc, min_vol_mult=abs_vol_mult, max_body_pct=abs_body) if show_abs else []
vwap_val = compute_vwap(ohlc) if show_vwap else None

# ====================== HEADER ======================
now = datetime.now()
st.markdown(f"""
<div class="hdr">
  <div>
    <span class="hdr-title">DEEP PROFILE</span>
    <span style="color:#2a2e39;margin:0 8px;">|</span>
    <span style="color:#d1d4dc;font-size:0.85rem;">{selected}</span>
    <span style="color:#2a2e39;margin:0 8px;">|</span>
    <span style="color:#787b86;font-size:0.7rem;">POC · VA · HVN · LVN · ABSORPTION · VWAP</span>
  </div>
  <div class="hdr-sub">{now.strftime('%Y-%m-%d %H:%M:%S')} IST</div>
</div>
""", unsafe_allow_html=True)

poc_s = f"{profile['poc']:.{dec}f}" if profile else "—"
vah_s = f"{profile['vah']:.{dec}f}" if profile else "—"
val_s = f"{profile['val']:.{dec}f}" if profile else "—"
dcls = "bull" if delta_px >= 0 else "bear"

st.markdown(f"""
<div class="ticker">
  <span style="color:#f0b90b;font-weight:700;">{yf_sym}</span>
  &nbsp;&nbsp;
  <span style="color:#fff;font-weight:700;font-size:1.05rem;">{last_px:,.{dec}f}</span>
  &nbsp;<span class="{dcls}">{delta_px:+.{dec}f} ({delta_pct:+.2f}%)</span>
  &nbsp;&nbsp;|&nbsp;&nbsp;
  POC <span class="poc">{poc_s}</span>
  &nbsp;|&nbsp;
  VAH <span class="vah">{vah_s}</span>
  &nbsp;|&nbsp;
  VAL <span class="val">{val_s}</span>
  &nbsp;|&nbsp;
  HVN <span class="hvn">{len(hvn_list)}</span>
  &nbsp;|&nbsp;
  LVN <span class="lvn">{len(lvn_list)}</span>
  &nbsp;|&nbsp;
  ABS <span class="amber">{len(absorptions)}</span>
  {"&nbsp;|&nbsp; VWAP <span class='amber'>" + f"{vwap_val:.{dec}f}" + "</span>" if vwap_val else ""}
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("LAST", f"{last_px:,.{dec}f}", f"{delta_px:+.{dec}f}")
m2.metric("POC", poc_s)
m3.metric("VAH", vah_s)
m4.metric("VAL", val_s)
m5.metric("HVN / LVN", f"{len(hvn_list)} / {len(lvn_list)}")
m6.metric("ABSORPTION", len(absorptions))

# ====================== MAIN CHART ======================
left, right = st.columns([1.7, 1])

with left:
    st.markdown('<div class="panel-t">VOLUME PROFILE CHART</div>', unsafe_allow_html=True)

    if chart_mode.startswith("TradingView"):
        html = f"""
        <div style="height:560px;width:100%;">
          <div id="tv_chart" style="height:100%;width:100%;"></div>
          <script src="https://s3.tradingview.com/tv.js"></script>
          <script>
          new TradingView.widget({{
            container_id: "tv_chart", width: "100%", height: 560,
            symbol: "{tv_sym}", interval: "{tv_tf}", timezone: "Asia/Kolkata",
            theme: "dark", style: "1", locale: "en", toolbar_bg: "#0b0e11",
            enable_publishing: false, hide_legend: false, support_host: "https://www.tradingview.com"
          }});
          </script>
        </div>
        """
        components.html(html, height=580)
        st.caption("Draw POC / VAH / VAL / HVN from the right panel onto TradingView.")
    else:
        if ohlc is None or len(ohlc) < 5:
            st.warning("No OHLC data — try refresh or another instrument.")
        else:
            fig = make_subplots(
                rows=1, cols=2,
                column_widths=[0.72, 0.28],
                shared_yaxes=True,
                horizontal_spacing=0.02,
            )

            # Candles
            fig.add_trace(go.Candlestick(
                x=ohlc["time"], open=ohlc["open"], high=ohlc["high"],
                low=ohlc["low"], close=ohlc["close"], name="OHLC",
                increasing_line_color="#26a69a", decreasing_line_color="#ef5350",
                increasing_fillcolor="#26a69a", decreasing_fillcolor="#ef5350",
            ), row=1, col=1)

            # VWAP line
            if show_vwap and vwap_val:
                fig.add_hline(y=vwap_val, line_dash="dot", line_color="#f0b90b",
                              line_width=1, annotation_text="VWAP", annotation_position="right", row=1, col=1)

            # POC / VA
            if profile:
                if show_poc:
                    fig.add_hline(y=profile["poc"], line_color="#e91e8c", line_width=1.5,
                                  annotation_text=f"POC {profile['poc']:.{dec}f}",
                                  annotation_position="left", row=1, col=1)
                if show_va:
                    fig.add_hline(y=profile["vah"], line_dash="dash", line_color="#26a69a", line_width=1,
                                  annotation_text="VAH", annotation_position="left", row=1, col=1)
                    fig.add_hline(y=profile["val"], line_dash="dash", line_color="#ef5350", line_width=1,
                                  annotation_text="VAL", annotation_position="left", row=1, col=1)
                    fig.add_hrect(y0=profile["val"], y1=profile["vah"],
                                  fillcolor="rgba(38,166,154,0.06)", line_width=0, row=1, col=1)

                # HVN bands
                if show_hvn:
                    for h in hvn_list[:5]:
                        fig.add_hline(y=h["price"], line_color="rgba(66,165,245,0.7)", line_width=1,
                                      line_dash="dot", row=1, col=1)

                # LVN
                if show_lvn:
                    for lv in lvn_list[:4]:
                        fig.add_hline(y=lv["price"], line_color="rgba(171,71,188,0.5)", line_width=1,
                                      line_dash="dot", row=1, col=1)

                # Volume profile histogram (horizontal)
                if show_vp:
                    colors = []
                    for i, dlt in enumerate(profile["delta"]):
                        if show_delta:
                            colors.append("#26a69a" if dlt >= 0 else "#ef5350")
                        else:
                            colors.append("#42a5f5")
                    # highlight POC bar
                    colors[profile["poc_idx"]] = "#e91e8c"

                    fig.add_trace(go.Bar(
                        x=profile["volume"],
                        y=profile["centers"],
                        orientation="h",
                        marker_color=colors,
                        opacity=0.75,
                        name="Volume Profile",
                        hovertemplate="Price %{y:." + str(dec) + "f}<br>Vol %{x:.0f}<extra></extra>",
                    ), row=1, col=2)

            # Absorption markers on price chart
            if show_abs and absorptions:
                abs_x, abs_y, abs_c, abs_t = [], [], [], []
                for a in absorptions:
                    abs_x.append(a["time"])
                    abs_y.append(a["price"])
                    abs_c.append("#26a69a" if a["side"] == "BUY" else "#ef5350")
                    abs_t.append(a["type"])
                fig.add_trace(go.Scatter(
                    x=abs_x, y=abs_y, mode="markers",
                    marker=dict(size=11, symbol="diamond", color=abs_c, line=dict(width=1, color="#fff")),
                    name="Absorption",
                    text=abs_t,
                    hovertemplate="%{text}<br>%{y:." + str(dec) + "f}<extra></extra>",
                ), row=1, col=1)

            fig.update_layout(
                template="plotly_dark",
                height=560,
                margin=dict(l=8, r=8, t=24, b=8),
                paper_bgcolor="#0b0e11",
                plot_bgcolor="#0b0e11",
                font=dict(family="Roboto Mono, monospace", color="#787b86", size=10),
                xaxis_rangeslider_visible=False,
                showlegend=False,
                hovermode="x unified",
            )
            fig.update_xaxes(showgrid=False, row=1, col=1)
            fig.update_xaxes(showgrid=False, title_text="Volume", row=1, col=2)
            fig.update_yaxes(showgrid=True, gridcolor="#1a1e28", row=1, col=1)
            fig.update_yaxes(showgrid=False, row=1, col=2)

            st.plotly_chart(fig, use_container_width=True)

with right:
    # Key levels panel
    st.markdown('<div class="panel-t">KEY LEVELS</div>', unsafe_allow_html=True)
    if profile:
        st.markdown(f"""
        <div class="panel">
          <div class="row"><span>POC</span><span class="poc">{profile['poc']:.{dec}f}</span></div>
          <div class="row"><span>VAH</span><span class="vah">{profile['vah']:.{dec}f}</span></div>
          <div class="row"><span>VAL</span><span class="val">{profile['val']:.{dec}f}</span></div>
          <div class="row"><span>VWAP</span><span class="amber">{f"{vwap_val:.{dec}f}" if vwap_val else "—"}</span></div>
          <div class="row"><span>VA %</span><span style="color:#787b86;">{int(va_pct*100)}%</span></div>
          <div class="row"><span>BINS</span><span style="color:#787b86;">{n_bins}</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.caption("Profile unavailable")

    # HVN
    st.markdown('<div class="panel-t">HVN — HIGH VOLUME NODES (PEAKS)</div>', unsafe_allow_html=True)
    if hvn_list:
        for h in hvn_list:
            st.markdown(f"""
            <div class="panel" style="border-left:3px solid #42a5f5;padding:6px 10px;margin-bottom:4px;">
              <div class="row"><span class="hvn">HVN</span><span style="color:#d1d4dc;font-weight:600;">{h['price']:.{dec}f}</span></div>
              <div class="row"><span>Volume share</span><span style="color:#787b86;">{h['pct']:.1f}%</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No HVN — lower sensitivity or more bars")

    # LVN
    st.markdown('<div class="panel-t">LVN — LOW VOLUME NODES (VALLEYS)</div>', unsafe_allow_html=True)
    if lvn_list:
        for lv in lvn_list:
            st.markdown(f"""
            <div class="panel" style="border-left:3px solid #ab47bc;padding:6px 10px;margin-bottom:4px;">
              <div class="row"><span class="lvn">LVN</span><span style="color:#d1d4dc;font-weight:600;">{lv['price']:.{dec}f}</span></div>
              <div class="row"><span>Volume share</span><span style="color:#787b86;">{lv['pct']:.1f}%</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No LVN detected")

    # Absorption
    st.markdown('<div class="panel-t">ABSORPTION</div>', unsafe_allow_html=True)
    if absorptions:
        for a in reversed(absorptions[-6:]):
            cls = "abs-buy" if a["side"] == "BUY" else "abs-sell"
            st.markdown(f"""
            <div class="panel" style="border-left:3px solid {'#26a69a' if a['side']=='BUY' else '#ef5350'};padding:6px 10px;margin-bottom:4px;">
              <div class="row"><span class="{cls}">{a['type']}</span><span style="color:#d1d4dc;">{a['price']:.{dec}f}</span></div>
              <div style="color:#787b86;font-size:0.7rem;">{a['note']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No absorption events — adjust filters")

# ====================== GUIDE ======================
with st.expander("HOW TO READ (Deepcharts-style)"):
    st.markdown("""
**POC (Point of Control)** — price with the most traded volume. Magnet / fair value.

**Value Area (VAH / VAL)** — zone containing X% of volume (default 70%). Acceptance zone.

**HVN (High Volume Node / Peak)** — heavy acceptance. Price often rotates or reacts here (support/resistance).

**LVN (Low Volume Node / Valley)** — thin volume. Price can move through quickly (imbalance / gap in interest).

**Absorption**
- **ASK ABSORPTION** — aggressive sells absorbed by buyers → possible bounce / support
- **BID ABSORPTION** — aggressive buys absorbed by sellers → possible rejection / resistance

**Settings tip**
- More bins = finer profile  
- Higher HVN sensitivity = fewer, stronger nodes  
- Higher min vol mult = only strong absorption events  

> Profile is built from Yahoo Finance OHLC+volume (not exchange tick data). For true order-flow delta, use a platform with CME/tick feeds.
""")

st.caption(f"Deep Profile Terminal · {yf_sym} · POC {poc_s} · VAH {vah_s} · VAL {val_s} · Signal only — no orders")

if auto:
    import time
    time.sleep(rate)
    st.rerun()
