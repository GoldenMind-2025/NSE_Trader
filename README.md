# NSE_Trader
Calculates Bullish and Bearish stock price deviations from 50 day moving average with standard deviations
# Stock Deviation Analyzer

A premium Streamlit tool to analyze NSE stock price deviations from the 50-day Moving Average (50-DMA) over a 30-month window.

## Features
- **30-Month Historical View**: High-fidelity data fetched via `yfinance`.
- **50-DMA Analysis**: Visual and numeric tracking of price vs. moving average.
- **Premium Metrics**: 
  - **Off Max-High**: Percentage drop from the highest close.
  - **Current MA Dev**: Real-time deviation from the 50-DMA.
  - **Max Bullish/Bearish Dev**: Historical extremes with Standard Deviation (σ).
- **Interactive Plotly Chart**: Zoomable and searchable price chart with a range slider.

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements_deviation_chart.txt
   ```

2. **Run the Application**:
   ```bash
   streamlit run deviation_chart.py
   ```

## Usage
- Enter any NSE ticker symbol in the input box (e.g., `ADANIPOWER`, `RELIANCE`, `TCS`). 
- The app automatically appends `.NS` for NSE data.

## Credits
Author: Golden_Mind - Jan 2026
Built with Python, Streamlit, and Plotly.
