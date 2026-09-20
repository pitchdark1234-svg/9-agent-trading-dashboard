# ⚡ 9-Agent AI Trading Command Center

Live multi-agent dashboard for **Gold**, **Crude Oil** & **Natural Gas**.

**Now connected to real market data** via Yahoo Finance (free, no API key).

---

## Features

- Real prices from Yahoo Finance futures: `GC=F` (Gold), `CL=F` (Crude), `NG=F` (Natural Gas)
- 9 specialized AI agents with live reasoning
- Final Decision Agent → Entry + Stop Loss + Take Profit
- Live charts with real recent price history
- Critical news & upcoming events panel
- Risk Manager with approval logic
- Dark professional UI

---

## 🚀 One-Click Deployment (Streamlit Cloud)

1. Create a public GitHub repository
2. Upload these files:
   - `trading_dashboard.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `README.md`
3. Go to https://share.streamlit.io → New app
4. Select your repo → Main file: `trading_dashboard.py` → Deploy

---

## Run Locally

```bash
pip install -r requirements.txt
streamlit run trading_dashboard.py
```

---

## Data Source

- **Yahoo Finance** via `yfinance` library (free, delayed data)
- Symbols: GC=F, CL=F, NG=F
- Falls back to simulation if data cannot be fetched
- Cached for 60 seconds to respect rate limits

## ⚠️ Disclaimer

This is for educational and research purposes only.  
Data is delayed. No real trades are executed.  
Trading involves substantial risk of loss.
