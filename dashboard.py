import os
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from pathlib import Path
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="TrendSense Dashboard", suppress_callback_exceptions=True)

BASE_PATH = Path("generated_data")

def load_data():
    return {
        "keywords": pd.read_csv(BASE_PATH / "trendsense_keywords.csv"),
        "consumer": pd.read_csv(BASE_PATH / "trendsense_consumer_behavior.csv"),
        "search_trends": pd.read_csv(BASE_PATH / "trendsense_search_trends.csv"),
        "predictions": pd.read_csv(BASE_PATH / "trendsense_market_predictions.csv"),
        "sales": pd.read_csv(BASE_PATH / "trendsense_sales_correlation.csv")
    }

app.layout = dbc.Container(fluid=True, children=[
    dbc.Row([
        dbc.Col(html.H2("📊 TrendSense: AI-Powered Market Trend Dashboard"), width=9),
        dbc.Col(html.Div(id="last-updated", className="text-end text-muted", style={"marginTop": "10px"}), width=3),
    ], className="align-items-center my-3"),

    dbc.Row([
        dbc.Col(dbc.Button("🔄 Reload Data", id="reload-button", color="primary", className="mb-2"), width="auto")
    ]),

    dcc.Tabs([
        dcc.Tab(label="Top Keywords", children=[
            dcc.Graph(id="top-keywords-chart", config={"displayModeBar": False}, style={"height": "50vh"}),
            dash_table.DataTable(
                id="keywords-table",
                page_size=10,
                style_table={"overflowX": "auto", "padding": "10px"},
                style_cell={"textAlign": "left", "padding": "5px"},
                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"}
            )
        ]),
        dcc.Tab(label="Search Trends Over Time", children=[
            dcc.Graph(id="search-trend-chart", config={"displayModeBar": False}, style={"height": "50vh"}),
            dash_table.DataTable(
                id="search-trends-table",
                page_size=10,
                style_table={"overflowX": "auto", "padding": "10px"},
                style_cell={"textAlign": "left", "padding": "5px"},
                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"}
            )
        ]),
        dcc.Tab(label="Market Predictions", children=[
            dcc.Graph(id="market-predictions-chart", config={"displayModeBar": False}, style={"height": "50vh"}),
            dash_table.DataTable(
                id="predictions-table",
                page_size=10,
                style_table={"overflowX": "auto", "padding": "10px"},
                style_cell={"textAlign": "left", "padding": "5px"},
                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"}
            )
        ]),
        dcc.Tab(label="Sales Correlation", children=[
            dcc.Graph(id="sales-correlation-chart", config={"displayModeBar": False}, style={"height": "50vh"}),
            dash_table.DataTable(
                id="sales-table",
                page_size=10,
                style_table={"overflowX": "auto", "padding": "10px"},
                style_cell={"textAlign": "left", "padding": "5px"},
                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"}
            )
        ]),
        dcc.Tab(label="Raw Data", children=[
            dash_table.DataTable(
                id="raw-keywords-table",
                page_size=20,
                style_table={"overflowX": "auto", "padding": "10px"},
                style_cell={"textAlign": "left", "padding": "5px"},
                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"}
            )
        ])
    ])
])

@app.callback(
    [
        Output("top-keywords-chart", "figure"),
        Output("search-trend-chart", "figure"),
        Output("market-predictions-chart", "figure"),
        Output("sales-correlation-chart", "figure"),
        Output("keywords-table", "data"),
        Output("keywords-table", "columns"),
        Output("search-trends-table", "data"),
        Output("search-trends-table", "columns"),
        Output("predictions-table", "data"),
        Output("predictions-table", "columns"),
        Output("sales-table", "data"),
        Output("sales-table", "columns"),
        Output("raw-keywords-table", "data"),
        Output("raw-keywords-table", "columns"),
        Output("last-updated", "children"),
    ],
    [Input("reload-button", "n_clicks")]
)
def update_dashboard(n_clicks):
    data = load_data()

    fig_top_keywords = px.bar(
        data["keywords"].sort_values("search_volume", ascending=False).head(10),
        x="keyword", y="search_volume", color="category",
        title="Top 10 Keywords by Search Volume"
    )
    fig_top_keywords.update_layout(margin=dict(t=50, b=30))

    top_keywords = data["keywords"].sort_values("search_volume", ascending=False).head(5)["keyword"].tolist()
    filtered_trends = data["search_trends"][data["search_trends"]["keyword"].isin(top_keywords)]
    fig_search_trends = px.line(
        filtered_trends, x="date", y="search_volume", color="keyword",
        title="Search Volume Trends for Top 5 Keywords"
    )
    fig_search_trends.update_layout(margin=dict(t=50, b=30))

    fig_predictions = px.scatter(
        data["predictions"], x="predicted_interest_30d", y="predicted_interest_90d",
        size="confidence_score", color="category", hover_name="keyword",
        title="Market Predictions: 30-day vs 90-day Interest"
    )
    fig_predictions.update_layout(margin=dict(t=50, b=30))

    fig_sales_corr = px.scatter(
        data["sales"], x="search_volume", y="sales_volume",
        size="conversion_rate", color="revenue",
        title="Sales Volume vs Search Volume with Conversion Rate"
    )
    fig_sales_corr.update_layout(margin=dict(t=50, b=30))

    keywords_data = data["keywords"].to_dict("records")
    keywords_columns = [{"name": col, "id": col} for col in data["keywords"].columns]

    search_trends_data = data["search_trends"].to_dict("records")
    search_trends_columns = [{"name": col, "id": col} for col in data["search_trends"].columns]

    predictions_data = data["predictions"].to_dict("records")
    predictions_columns = [{"name": col, "id": col} for col in data["predictions"].columns]

    sales_data = data["sales"].to_dict("records")
    sales_columns = [{"name": col, "id": col} for col in data["sales"].columns]

    
    raw_data = data["keywords"].to_dict("records")
    raw_columns = [{"name": col, "id": col} for col in data["keywords"].columns]

    return (
        fig_top_keywords,
        fig_search_trends,
        fig_predictions,
        fig_sales_corr,
        keywords_data,
        keywords_columns,
        search_trends_data,
        search_trends_columns,
        predictions_data,
        predictions_columns,
        sales_data,
        sales_columns,
        raw_data,
        raw_columns,
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=True, host="0.0.0.0", port=port)

