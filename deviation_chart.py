import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import numpy as np
from datetime import datetime, timedelta

# =====================================================================
#  CONFIGURATION
# =====================================================================
st.set_page_config(page_title="Stock Deviation Analysis", layout="wide")

WINDOW_MONTHS = 30
MA_PERIOD = 50

# =====================================================================
#  STYLING (Premium aesthetics)
# =====================================================================
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    .premium-card {
        background: #8FD9FB;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        color: #000000;
        margin-bottom: 20px;
        border: 1px solid #d1d5db;
    }
    .header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        margin-bottom: 10px;
    }
    .header-title {
        font-size: 24px;
        font-weight: 700;
    }
    .price-tag {
        background: #ffffff;
        padding: 8px 12px;
        border-radius: 10px;
        font-size: 18px;
        color: #111827;
        font-weight: 700;
    }
    .header-date {
        font-size: 16px;
        font-weight: 400;
        margin-bottom: 5px;
    }
    .metrics-grid {
        display: flex;
        gap: 20px;
        margin-top: 15px;
    }
    .metric-item {
        background: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        flex: 1;
        min-width: 0;
    }
    .metric-label {
        font-size: 12px;
        color: #4b5563;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 22px;
        font-weight: 700;
    }
    .std-dev-val {
        font-size: 14px;
        font-weight: 600;
        color: #6b7280;
        margin-top: 5px;
    }
    .green { color: #059669; }
    .red { color: #dc2626; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
#  DATA LOGIC
# =====================================================================
def get_stock_data(symbol):
    ticker = f"{symbol.upper()}.NS"
    end_date = datetime.today()
    start_date = end_date - timedelta(days=WINDOW_MONTHS * 30)
    
    try:
        t_obj = yf.Ticker(ticker)
        hist = t_obj.history(start=start_date, end=end_date + timedelta(days=1)).reset_index()
        info = t_obj.info
        name = info.get("longName", symbol.upper())
        return hist, name, info.get("regularMarketPrice", 0.0)
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame(), symbol, 0.0

def calculate_metrics(hist, price_now):
    if hist.empty:
        return None
    
    hist = hist.copy()
    hist["MA50"] = hist["Close"].rolling(MA_PERIOD).mean()
    
    # Use only rows where MA is valid
    valid_hist = hist[hist["MA50"].notna()].copy()
    if valid_hist.empty:
        return None
    
    valid_hist["pct_dev"] = 100 * (valid_hist["Close"] - valid_hist["MA50"]) / valid_hist["MA50"]
    
    current_ma = valid_hist["MA50"].iloc[-1]
    pct_dev = 100 * (price_now - current_ma) / current_ma if current_ma != 0 else 0
    
    max_dev = valid_hist["pct_dev"].max()
    min_dev = valid_hist["pct_dev"].min()
    pos_std = valid_hist[valid_hist["pct_dev"] > 0]["pct_dev"].std()
    neg_std = valid_hist[valid_hist["pct_dev"] < 0]["pct_dev"].std()
    
    max_close = hist["Close"].max()
    off_high = 100 * (price_now - max_close) / max_close if max_close != 0 else 0
    
    return {
        "price_now": price_now,
        "max_high": max_close,
        "off_high": off_high,
        "current_ma_dev": pct_dev,
        "max_bullish_dev": max_dev,
        "max_bearish_dev": min_dev,
        "pos_std": pos_std,
        "neg_std": neg_std,
        "hist": hist
    }

# =====================================================================
#  UI COMPONENTS
# =====================================================================
def render_header(symbol, name, metrics):
    today_str = datetime.now().strftime("%d %b %Y")
    
    off_high_color = "red" if metrics["off_high"] < 0 else "green"
    ma_dev_color = "green" if metrics["current_ma_dev"] > 0 else "red"
    
    st.markdown(f"""
    <div class="premium-card">
        <div class="header-date">{today_str}</div>
        <div class="header-row">
            <div class="header-title">
                {name} <span style="font-weight:400; color:#4b5563; font-size:18px;">({symbol.upper()})</span>
            </div>
            <div class="price-tag">
                <span style="font-weight:400; color:#4b5563; font-size:14px;">Price now</span> 
                ₹{metrics['price_now']:,.2f}
            </div>
        </div>
        <div class="metrics-grid">
            <div class="metric-item">
                <div class="metric-label">Off Max-High</div>
                <div class="metric-value {off_high_color}">{metrics['off_high']:+.2f}%</div>
                <div style="font-size:14px; color:#4b5563;">Max: ₹{metrics['max_high']:,.0f}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Current MA Dev</div>
                <div class="metric-value {ma_dev_color}">{metrics['current_ma_dev']:+.2f}%</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Max Bullish Dev</div>
                <div class="metric-value green">{metrics['max_bullish_dev']:+.2f}%</div>
                <div class="std-dev-val">σ: {metrics['pos_std']:.2f}%</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Max Bearish Dev</div>
                <div class="metric-value red">{metrics['max_bearish_dev']:+.2f}%</div>
                <div class="std-dev-val">σ: {metrics['neg_std']:.2f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_chart(hist):
    fig = go.Figure()
    fig.add_scatter(x=hist["Date"], y=hist["Close"], name="Close", line=dict(color="#2563eb", width=2))
    fig.add_scatter(x=hist["Date"], y=hist["MA50"], name="50 DMA", line=dict(color="#d97706", width=2, dash="dot"))
    
    fig.update_layout(
        height=600,
        hovermode="x unified",
        margin=dict(t=30, b=30, l=30, r=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(type="date", rangeslider=dict(visible=True), gridcolor="#f3f4f6"),
        yaxis=dict(title="Price (₹)", gridcolor="#f3f4f6"),
        plot_bgcolor="white"
    )
    st.plotly_chart(fig, use_container_width=True)

# =====================================================================
#  MAIN APP
# =====================================================================
def main():
    inject_css()
    
    st.subheader("📈 Stock Deviation Analyzer")
    st.write("by Golden_Mind")
    
    symbol = st.text_input("Enter NSE Symbol (e.g. ADANIPOWER, RELIANCE, TCS):", value="ADANIPOWER").strip()
    
    if symbol:
        with st.spinner(f"Fetching data for {symbol}..."):
            hist, name, price_now = get_stock_data(symbol)
            
            if not hist.empty:
                metrics = calculate_metrics(hist, price_now)
                
                if metrics:
                    render_header(symbol, name, metrics)
                    render_chart(metrics["hist"])
                else:
                    st.error("Insufficient data to calculate moving average and metrics.")
            else:
                st.error("Could not find data for this symbol. Please check if it is a valid NSE ticker.")

if __name__ == "__main__":
    main()
