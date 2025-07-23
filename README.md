# python_dashboard

📊 Python Stock Dashboard

Overview

This is a mini interactive dashboard built using Dash and Plotly, showcasing live performance metrics for three sample stocks — JPM, NFLX, and BA — along with a custom-weighted portfolio.


---

Key Features

Live Data Updates
Real-time data is pulled dynamically from Yahoo Finance via the yfinance API. The dashboard automatically captures recent prices and returns on each load.

---

Portfolio Weighting
A simple portfolio allocation is used:

JPM: 40%

NFLX: 30%

BA: 30%
These weights are applied across all metrics and visualizations.

---


Comprehensive Metrics
A total of 12 core metrics are calculated and displayed:

Price & Returns: Adjusted closing price, daily return, correlation, and cumulative return (both for individual tickers and the portfolio)

Risk Metrics: Drawdowns, rolling 30-day volatility, rolling 30-day Sharpe ratio, rolling 30-day VaR (95%), and rolling 30-day correlation

---



Interactive KPIs & Graphs


Homepage: Live price KPIs and vertical card layout for daily & cumulative returns

Performance Metrics Page: KPIs for cumulative returns and interactive graphs (adjusted price, cumulative returns, drawdowns, correlation)

Rolling Metrics Page: KPIs and scrollable charts for rolling volatility, Sharpe, VaR, and rolling correlations

About Page: Context on dashboard features, stock selection, and metric definitions


---


Responsive & User-Friendly Layout
Built with Bootstrap components for a clean design.
Sidebar navigation with pages like Home, Performance Metrics, Rolling Metrics, and About.
KPI cards remain fixed while graphs are scrollable.


---


Dashboard link: https://minidashboard.onrender.com
