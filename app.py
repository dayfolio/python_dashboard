
#### mini dashboard

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Initialize app
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Mini Dashboard"
server = app.server


# --- Utility Function ---
def get_live_data():
    tickers = ['JPM', 'NFLX', 'BA']
    weights = [0.4, 0.3, 0.3]

    raw_data = yf.download(tickers, period="10y", interval="1d", group_by='ticker', auto_adjust=True)

    if isinstance(raw_data.columns, pd.MultiIndex):
        price_data = pd.concat([raw_data[ticker]["Close"] for ticker in tickers], axis=1)
        price_data.columns = tickers
    else:
        price_data = raw_data['Close']

    price_data = price_data.dropna()
    returns = price_data.pct_change().dropna()
    cumulative_returns = (1 + returns).cumprod()
    portfolio_prices = (price_data * weights).sum(axis=1)
    portfolio_returns = portfolio_prices.pct_change().dropna()
    portfolio_cumulative = (1 + portfolio_returns).cumprod()
    drawdowns = cumulative_returns / cumulative_returns.cummax() - 1

    latest_prices = price_data.iloc[-1]
    daily_returns = returns.iloc[-1]
    cumulative_returns_latest = cumulative_returns.iloc[-1]

    return (
        latest_prices, daily_returns, cumulative_returns, cumulative_returns_latest,
        portfolio_cumulative, drawdowns, returns, price_data,
        portfolio_prices, portfolio_returns
    )

(
    latest_prices, daily_returns, cumulative_returns, cumulative_returns_latest,
    portfolio_cumulative, drawdowns, returns, price_data,
    portfolio_prices, portfolio_returns
) = get_live_data()

# 💡 Define rolling metrics cleanly here
rolling_volatility = returns.rolling(window=30).std()
rolling_volatility["Portfolio"] = portfolio_returns.rolling(window=30).std()

rolling_sharpe = returns.rolling(window=30).mean() / returns.rolling(window=30).std()
rolling_sharpe["Portfolio"] = portfolio_returns.rolling(window=30).mean() / portfolio_returns.rolling(window=30).std()

rolling_var = returns.rolling(window=30).quantile(0.05)
rolling_var["Portfolio"] = portfolio_returns.rolling(window=30).quantile(0.05)

# Optional: precompute current + avg for KPIs
latest_vol = rolling_volatility.iloc[-1]
avg_vol = rolling_volatility.mean()

latest_sharpe = rolling_sharpe.iloc[-1]
avg_sharpe = rolling_sharpe.mean()

latest_var = rolling_var.iloc[-1]
avg_var = rolling_var.mean()




# --- Color Themes ---
kpi_colors = ["#364c84", "#95b1ee", "#fffdf5"]
pastel_colors = ["#364c84", "#95b1ee", "#fffdf5"]
ticker_colors = {
    "JPM": "#b8b8f3",
    "NFLX": "#7db9e8",
    "BA": "#003f5c" }
ticker_fillcolors = {
    "JPM": "rgba(184, 184, 243, 0.2)",
    "NFLX": "rgba(125, 185, 232, 0.2)",
    "BA": "rgba(0, 63, 92, 0.2 )"
}
rolling_colors = {
    "JPM": "#b8b8f3",
    "NFLX": "#7db9e8",
    "BA": "#003f5c",
    "Portfolio": "#111111"
}
rolling_fillcolors = {
    "JPM": "rgba(184, 184, 243, 0.2)",
    "NFLX": "rgba(125, 185, 232, 0.2)",
    "BA": "rgba(0, 63, 92, 0.2)",
    "Portfolio": "rgba(0, 0, 0, 0.1)"
}

tickers = ['JPM', 'NFLX', 'BA']
weights = [0.4, 0.3, 0.3]

def calculate_drawdowns(cumulative_returns):
    return (cumulative_returns / cumulative_returns.cummax()) - 1

# --- KPI Cards ---
def kpi_card(title, value, color):
    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="card-title text-center mb-2"),
            html.H4(value, className="card-text text-center")
        ])
    ], style={"backgroundColor": color, "border": "none", "borderRadius": "10px"})

def generate_price_kpis():
    return dbc.Row([
        dbc.Col(kpi_card(f"{ticker} Price", f"${latest_prices[ticker]:.2f}", kpi_colors[i]), width=4)
        for i, ticker in enumerate(tickers)
    ], justify="between", className="mb-4")

def return_kpi_group(ticker, color):
    cum_return = cumulative_returns_latest[ticker]
    daily_return = daily_returns[ticker]
    return dbc.Card([
        dbc.CardBody([
            html.H6(f"{ticker} Returns", className="card-title text-center"),
            html.P(f"Daily: {daily_return * 100:.2f}%", className="card-text text-center mb-2"),
            html.P(f"Cumulative: {(cum_return - 1) * 100:.2f}%", className="card-text text-center")
        ])
    ], style={"backgroundColor": color, "border": "none", "borderRadius": "10px", "marginBottom": "20px", "height": "170px"})

def stacked_return_kpis():
    return dbc.Col([
        return_kpi_group(tickers[0], pastel_colors[0]),
        return_kpi_group(tickers[1], pastel_colors[1]),
        return_kpi_group(tickers[2], pastel_colors[2])
    ], width=2)

def generate_metrics_horizontal_kpis():
    return dbc.Row([
        dbc.Col(kpi_card(
            f"{ticker} Cumulative Return",
            f"{(cumulative_returns_latest[ticker] - 1) * 100:.2f}%",
            pastel_colors[i]
        ), width=4)
        for i, ticker in enumerate(tickers)
    ], justify="between", className="mb-4")

def return_kpi_group(ticker, color):
    return dbc.Card([
        dbc.CardBody([
            html.H6(f"{ticker} Metrics", className="card-title text-center"),
            html.P(f"Adj Close: ${latest_prices[ticker]:.2f}", className="card-text text-center mb-2"),
            html.P(f"Drawdown: {drawdowns[ticker].iloc[-1] * 100:.2f}%", className="card-text text-center")
        ])
    ], style={
        "backgroundColor": color,
        "border": "none",
        "borderRadius": "10px",
        "marginBottom": "20px",
        "height": "150px",
        "width":"100%"
    })

def generate_metrics_vertical_kpis():
    return dbc.Col([
        return_kpi_group(tickers[0], pastel_colors[0]),
        return_kpi_group(tickers[1], pastel_colors[1]),
        return_kpi_group(tickers[2], pastel_colors[2])
    ], width=2, style={"paddingRight": "0", "marginRight":"0"})

def generate_rolling_volatility_kpis(latest_vol, avg_vol, colors):
    return dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H6(f"{ticker} Rolling Volatility", className="card-title text-center"),
                    html.P(f"Latest: {latest_vol[ticker]*100:.2f}%", className="card-text text-center mb-1"),
                    html.P(f"Avg: {avg_vol[ticker]*100:.2f}%", className="card-text text-center")
                ])
            ], style={"backgroundColor": colors[i], "border": "none", "borderRadius": "10px"}),
            width=4
        )
        for i, ticker in enumerate(tickers + ["Portfolio"])
    ], className="mb-4", justify="between")

def return_rolling_kpi_group(ticker, color):
    try:
        sharpe_avg = rolling_sharpe[ticker].mean()
        sharpe_latest = rolling_sharpe[ticker].iloc[-1]
        var_avg = rolling_var[ticker].mean() * 100
        var_latest = rolling_var[ticker].iloc[-1] * 100
    except Exception as e:
        sharpe_avg = sharpe_latest = var_avg = var_latest = None

    return dbc.Card([
        dbc.CardBody([
            html.H6(f"{ticker}", className="card-title text-center"),
            html.P(f"Sharpe Avg: {sharpe_avg:.2f}" if sharpe_avg is not None else "Sharpe Avg: N/A", className="card-text text-center"),
            html.P(f"Sharpe Latest: {sharpe_latest:.2f}" if sharpe_latest is not None else "Sharpe Latest: N/A", className="card-text text-center"),
            html.P(f"VaR Avg: {var_avg:.2f}%" if var_avg is not None else "VaR Avg: N/A", className="card-text text-center"),
            html.P(f"VaR Latest: {var_latest:.2f}%" if var_latest is not None else "VaR Latest: N/A", className="card-text text-center")
        ])
    ], style={
        "backgroundColor": color,
        "border": "none",
        "borderRadius": "10px",
        "marginBottom": "0px",
        "height": "190px"
    })

def stacked_rolling_return_kpis():
    return dbc.Col([
        return_rolling_kpi_group("JPM", pastel_colors[0]),
        return_rolling_kpi_group("NFLX", pastel_colors[1]),
        return_rolling_kpi_group("BA", pastel_colors[2]),
        return_rolling_kpi_group("Portfolio", "#f4e2d8")
    ], width=2, style={"paddingRight": "0", "marginRight":"0"})



adjusted_close_figure = go.Figure()
for ticker in tickers:
    adjusted_close_figure.add_trace(go.Scatter(
        x=price_data.index,
        y=price_data[ticker],
        name=ticker,
        line=dict(width=3, color=ticker_colors[ticker]),
        fill='tozeroy',
        fillcolor=ticker_fillcolors[ticker]
    ))
adjusted_close_figure.update_layout(title=dict(text="Adjusted Close Prices", x=0.5, xanchor= 'center'), plot_bgcolor="#fffdf5", height = 350, margin=dict(l=10, r=10, t=40, b=10), legend=dict(x=0.15, y=1.00, orientation="h"))

cumulative_returns_figure = go.Figure()
for ticker in tickers:
    cumulative_returns_figure.add_trace(go.Scatter(
        x=cumulative_returns.index,
        y=cumulative_returns[ticker],
        name=ticker,
        line=dict(width=3, color=ticker_colors[ticker]),
        fill='tozeroy',
        fillcolor=ticker_fillcolors[ticker]
    ))
cumulative_returns_figure.update_layout(title=dict(text="Cumulative Returns", x=0.5, xanchor='center'), plot_bgcolor="#fffdf5", height = 350, margin=dict(l=10, r=10, t=40, b=10), legend=dict(x=0.15, y=1.00, orientation="h"))

drawdowns = calculate_drawdowns(cumulative_returns)
drawdowns_figure = go.Figure()
for ticker in tickers:
    drawdowns_figure.add_trace(go.Scatter(
        x=drawdowns.index,
        y=drawdowns[ticker],
        name=ticker,
        line=dict(width=3, color=ticker_colors[ticker])
    ))
drawdowns_figure.update_layout(title=dict(text="Drawdowns", x=0.5, xanchor='center'),  plot_bgcolor="#fffdf5", height = 350, margin=dict(l=10, r=10, t=40, b=10), legend=dict(x=0.25, y=1.06, orientation="h"))

correlation = returns.corr()
correlation_figure = go.Figure(data=go.Heatmap(
    z=correlation.values,
    x=correlation.columns,
    y=correlation.index,
    colorscale='blues'
))
correlation_figure.update_layout(title=dict(text="Correlation Matrix", x=0.5, xanchor='center'), plot_bgcolor="#fffdf5", height = 350, margin=dict(l=10, r=10, t=40, b=10))


# --- Portfolio Graph ---
def portfolio_graph():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio_cumulative.index,
        y=portfolio_cumulative,
        name='Portfolio',
        line=dict(color='black', width=3),
        fill='tozeroy',
        fillcolor='rgba(0,0,0,0.05)'
    ))
    
    
    for i, ticker in enumerate(tickers):
        fig.add_trace(go.Scatter(
            x=cumulative_returns.index,
            y=cumulative_returns[ticker],
            name=ticker,
            line=dict(width=2, color=ticker_colors[ticker])
        ))
    
    ## 
    


    fig.update_layout(title=dict(text="Portfolio Performance", x=0.5), margin=dict(t=60, b=20), height=400, 
        plot_bgcolor = "#fffdf5",
        paper_bgcolor="#bcd3f9",
        legend=dict(orientation="h", x=0.5, xanchor="center", y=0.99),template="plotly_white")
    return dcc.Graph(figure=fig)

rolling_vol_fig = go.Figure()
for t in rolling_volatility.columns:
    rolling_vol_fig.add_trace(go.Scatter(
        x=rolling_volatility.index,
        y=rolling_volatility[t],
        name=t,
        line=dict(color=rolling_colors[t], width=3),
        fill='tozeroy',
        fillcolor=rolling_fillcolors[t]
    ))
rolling_vol_fig.update_layout(
    title=dict(text="30-Day Rolling Volatility", x=0.5),
    plot_bgcolor="#fffdf5", margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(orientation="v", y=0.95, x=0.17, xanchor='center')
)

rolling_sharpe_fig = go.Figure()
for t in rolling_sharpe.columns:
    rolling_sharpe_fig.add_trace(go.Scatter(
        x=rolling_sharpe.index,
        y=rolling_sharpe[t],
        name=t,
        line=dict(color=rolling_colors[t], width=3),
        fill='tozeroy'
    ))
rolling_sharpe_fig.update_layout(
    title=dict(text="30-Day Rolling Sharpe Ratio", x=0.5),
    plot_bgcolor="#fffdf5", margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(orientation="h", y=1.02, x=0.5, xanchor='center')
)

rolling_var_fig = go.Figure()
for t in rolling_var.columns:
    rolling_var_fig.add_trace(go.Scatter(
        x=rolling_var.index,
        y=rolling_var[t],
        name=t,
        line=dict(color=rolling_colors[t], width=3),
        fill='tozeroy'
    ))
rolling_var_fig.update_layout(
    title=dict(text="30-Day Rolling VaR (95%)", x=0.5),
    plot_bgcolor="#fffdf5", margin=dict(l=10, r=10, t=40, b=10), height = 450,
    legend=dict(orientation="v", y=0.06, x=0.17, xanchor='center')
)

rolling_corr_fig = go.Figure()

# Define the pairs
correlation_pairs = [
    ("JPM", "NFLX"),
    ("JPM", "BA"),
    ("NFLX", "BA"),
    ("JPM", "Portfolio"),
    ("NFLX", "Portfolio"),
    ("BA", "Portfolio")
]

# Define custom line and fill colors
pair_colors = {
    ("JPM", "NFLX"): ("#b8b8f3", "rgba(184, 184, 243, 0.2)"),
    ("JPM", "BA"): ("#7db9e8", "rgba(125, 185, 232, 0.2)"),
    ("NFLX", "BA"): ("#003f5c", "rgba(0, 63, 92, 0.2)"),
    ("JPM", "Portfolio"): ("#cc8963", "rgba(204, 137, 99, 0.2)"),
    ("NFLX", "Portfolio"): ("#a1c181", "rgba(161, 193, 129, 0.2)"),
    ("BA", "Portfolio"): ("#6f1d1b", "rgba(111, 29, 27, 0.2)")
}

# Loop through each pair and compute rolling correlation
for t1, t2 in correlation_pairs:
    series1 = returns[t1]
    series2 = portfolio_returns if t2 == "Portfolio" else returns[t2]

    rolling_corr = series1.rolling(30).corr(series2)

    color, fill = pair_colors[(t1, t2)]
    rolling_corr_fig.add_trace(go.Scatter(
        x=rolling_corr.index,
        y=rolling_corr,
        name=f"{t1}–{t2}",
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=fill
    ))

# Layout
rolling_corr_fig.update_layout(
    title=dict(text="30-Day Rolling Correlation", x=0.5),
    plot_bgcolor="#fffdf5",
    legend=dict(orientation="h", y=0.15, x=0.5, xanchor='center'),
    margin=dict(l=10, r=10, t=40, b=10),
    height=450 )



# --- Sidebar ---
sidebar = html.Div([ 
    html.H2("Dashboard", className="display-5", style={"color": "white"}),
    html.Hr(),

    dbc.Nav([
        dbc.NavLink("Home", href="/", active="exact"),
        dbc.NavLink("Performance Metrics", href="/metrics", active="exact"),
        dbc.NavLink("Rolling Metrics", href="/rolling", active="exact"),
        dbc.NavLink("About", href="/about", active="exact")
    ], vertical=True, pills=True),

    html.Div(  # GitHub button section
        dbc.Button(
            "GitHub ↗",
            href="https://github.com/YOUR_GITHUB_PROFILE",  # ← Replace this
            color="light",
            target="_blank",
            style={"width": "100%"}
        ),
        style={
            "marginTop": "auto",
            "paddingTop": "1.5rem",
            "textAlign": "center"
        }
    )
],
style={
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "backgroundColor": "#001f3f",
    "display": "flex",
    "flexDirection": "column"
})

# --- Page Layouts ---
home_layout = html.Div([
    dbc.Container([
        html.Div(style={"height": "40px"}),  # Top Spacer
        generate_price_kpis(),
        dbc.Row([
            dbc.Col(portfolio_graph(), width=10),
            stacked_return_kpis()
        ], style={"marginBottom": "20px"}),
        html.P("* Portfolio shows cumulative performance for past year with weights: JPM: 40%, NFLX: 30%, BA: 30%",
               style={"fontSize": "13px", "color": "gray", "textAlign": "left", "marginTop": "-10px"})
    ], style={"margin": "0","paddingLeft":"2rem", "paddingRight": "2rem", "overflowX": "hidden"})
])

metrics_layout = html.Div([
    dbc.Container([
        html.H2("PERFORMANCE METRICS",
        className="text-center mb-4", style={"fontWeight":"bold"}),
        # Horizontal KPI row (Cumulative Returns)
        dbc.Row([
            dbc.Col(kpi_card(f"{ticker} Cumulative Return", 
                             f"{(cumulative_returns_latest[ticker] - 1) * 100:.2f}%", 
                             pastel_colors[i]), width=4)
            for i, ticker in enumerate(tickers)
        ], justify="between", className="mb-4", style={"marginTop": "20px"}),

        # Scrollable graph + fixed vertical KPI column
        dbc.Row([
            dbc.Col([
                html.Div([
                    dbc.Row([
                        dbc.Col(dcc.Graph(figure=adjusted_close_figure), width=6),
                        dbc.Col(dcc.Graph(figure=cumulative_returns_figure), width=6)
                    ], className="mb-4", style={"margin": "0"}),

                    dbc.Row([
                        dbc.Col(dcc.Graph(figure=drawdowns_figure), width=6),
                        dbc.Col(dcc.Graph(figure=correlation_figure), width=6)
                    ], className="mb-4", style={"margin": "0"},
                    )
                ], style={"height": "75vh", "overflowY": "auto", "paddingRight": "10px"})
            ], width=10),

            # Fixed vertical KPIs
            dbc.Col([
                return_kpi_group("JPM", pastel_colors[0]),
                return_kpi_group("NFLX", pastel_colors[1]),
                return_kpi_group("BA", pastel_colors[2])
            ], width=2, style={"position": "sticky", "top": "80px", "zIndex": 999})
        ])
    ], fluid=True, style={"marginLeft": "0rem", "marginRight": "1rem", "padding": "2rem"})
])




rolling_layout = html.Div([
    dbc.Container([
        html.H2("ROLLING METRICS",
                className="text-center mb-4", style={"fontWeight": "bold"}),

        # Horizontal KPI row (Rolling Volatility Avg & Latest)
        dbc.Row([
            dbc.Col(kpi_card(f"{ticker} Rolling Volatility", 
                             f"Avg: {rolling_volatility[ticker].mean():.2%} | Latest: {rolling_volatility[ticker].iloc[-1]:.2%}", 
                             pastel_colors[i]), width=4)
            for i, ticker in enumerate(tickers)
        ], justify="between", className="mb-4", style={"marginTop": "20px"}),

        # Scrollable graph section + fixed vertical KPIs
        dbc.Row([
            # Left: Scrollable graph section
            dbc.Col([
                html.Div([
                    dbc.Row([
                        dbc.Col(dcc.Graph(figure=rolling_vol_fig), width=6),
                        dbc.Col(dcc.Graph(figure=rolling_sharpe_fig), width=6)
                    ], className="mb-4", style={"margin": "0"}),

                    dbc.Row([
                        dbc.Col(dcc.Graph(figure=rolling_var_fig), width=6),
                        dbc.Col(dcc.Graph(figure=rolling_corr_fig), width=6)
                    ], className="mb-4", style={"margin": "0"}),
                ], style={"height": "100vh", "overflowY": "auto", "paddingRight": "10px"})
            ], width=10),

            # Right: Fixed vertical KPI stack
            dbc.Col([
                return_rolling_kpi_group("Portfolio", "#f4e2d8"),
                return_rolling_kpi_group("JPM", pastel_colors[0]),
                return_rolling_kpi_group("NFLX", pastel_colors[1]),
                return_rolling_kpi_group("BA", pastel_colors[2])
            ], width=2, style={"position": "sticky", "top": "10px", "zIndex": 999}),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H6("*Source: Yahoo Finance", style={"fontSize":"14px", "marginBottom":"0px"})
                    ])
                ])
            ])
        ])
    ], fluid=True, style={"marginLeft": "1rem", "marginRight": "1rem", "padding": "1rem"})
])

















about_layout = html.Div([
    dbc.Container([
        html.H2("ABOUT DASHBOARD", className="text-center mb-5", style={"fontWeight": "bold"}),

        # About Dashboard
        html.Div([
            html.H5("About dashboard", style={"fontWeight": "bold", "marginBottom": "10px"}),
            html.P("This is a mini dashboard designed to monitor live performance metrics for three selected sample stocks — JPMorgan Chase (JPM), Netflix (NFLX), and Boeing (BA). It offers both ticker-specific and portfolio-level insights through a snapshot of portfolio performance, stock-level insights, and risk-adjusted behavior through a fully interactive layout. The dashboard uses historical data spanning the past 10 years, to reflect a long-term perspective while also offering short-term and real-time insights via dynamic data update function."),
        ], className="mb-4"),

        # Live Financial Data
        html.Div([
            html.H5("Live financial data", style={"fontWeight": "bold", "marginBottom": "10px"}),
            html.P("All prices and returns displayed across the dashboard are sourced in real time from Yahoo Finance using the yfinance API. Adjustments for dividends and stock splits are incorporated directly at the data ingestion stage through automatic parameterization. Each time the dashboard is loaded, it fetches the most recent market data, ensuring that the computations reflect current conditions without relying on static or outdated sources."),
        ], className="mb-4"),

        # Stocks
        html.Div([
            html.H5("Stocks", style={"fontWeight": "bold", "marginBottom": "10px"}),
            html.P("The chosen stocks span three distinct industries: banking and finance, technology & media, and aerospace and defense to allow for a natural diversification of the portfolio. It also facilitates insights into how different industries respond to market fluctuations. This selection offers contrast in volatility profiles and economic sensitivity."),
        ], className="mb-4"),

        # Weight Allocation
        html.Div([
            html.H5("Weight allocation", style={"fontWeight": "bold", "marginBottom": "10px"}),
            html.P("The custom portfolio is constructed using weighted allocations: JPM: 40%; NFLX: 30%; BA: 30%. These weights apply across return calculations, cumulative metrics, and risk estimations."),
        ], className="mb-4"),

        # Metrics
        html.Div([
            html.H5("Metrics", style={"fontWeight": "bold", "marginBottom": "10px"}),
            html.P("The dashboard calculates twelve distinct metrics to capture various dimensions of performance and risk. These include adjusted closing prices, daily returns, cumulative returns, portfolio cumulative returns, drawdowns, and correlation matrices, as well as rolling 30-day volatility, rolling 30-day Sharpe ratios, rolling 30-day value at risk at a 95% confidence level, and rolling pairwise correlations between the tickers and the portfolio."),
        ], className="mb-4"),

        # KPIs
        html.Div([
            html.H5("KPIs", style={"fontWeight": "bold", "marginBottom": "10px"}),
            html.P("Each page of the dashboard includes dedicated key performance indicators tailored to the focus of that section. These indicators condense key information into at-a-glance summaries."),
            html.P("Homepage KPIs:\n • Horizontal: current prices for all stocks (live)\n • Vertical: daily and cumulative returns"),
            html.P("Performance metrics page KPIs:\n • Horizontal: cumulative returns (latest)\n • Vertical: adjusted close price and drawdowns"),
            html.P("Rolling metrics page KPIs:\n • Horizontal: rolling 30-day volatility (average and latest)\n • Vertical: rolling Sharpe ratio and rolling value at risk (average and latest)"),
        ], className="mb-4"),

        # Graphs
        html.Div([
            html.H5("Graphs", style={"fontWeight": "bold", "marginBottom": "10px"}),
            html.P("The dashboard features interactive graphs to visually summarize the performance and risk profiles for each ticker and the weighted portfolio. Overall, the dashboard visualizes the following metrics: adjusted close price trends, cumulative returns, portfolio return curves, drawdown paths, and correlation matrices, 30-day rolling volatility, rolling Sharpe ratios, value at risk, and rolling pairwise correlations, including correlations between each ticker and the portfolio. All graphs include color-coded traces and shaded areas beneath each line to enhance readability and visual context. The interactive features allow for zooming, panning, hovering data for deeper exploration, selection and deselection of tickers."),
        ], className="mb-5"),


    ], fluid=True, style={"marginLeft": "0.6rem", "marginRight": "1rem", "padding": "0rem"})
])


# --- App Layout ---
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    html.Div(id="page-content", style = {
        "marginLeft": "16rem", "padding":"0","overflowX":"hidden","width":"calc(100vw-16rem)","maxWidth":"calc(100vw-16rem)"
        })
], style={"overflowX":"hidden","margin":"0", "padding":"0", "width":"100vw", "maxWidth":"100vw"
})

# --- Callback ---
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/metrics":
        return metrics_layout
    elif pathname == "/rolling":
        return rolling_layout
    elif pathname == "/about":
        return about_layout
    return home_layout

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)
