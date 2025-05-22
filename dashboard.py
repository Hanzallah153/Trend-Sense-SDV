import os
import csv
from dash import Dash, dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="TrendSense Dashboard")

BASE_PATH = Path("generated_data")

def read_csv_dict(filename):
    with open(BASE_PATH / filename, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def get_bar_chart(data, x_key, y_key, title):
    x = [row[x_key] for row in data]
    y = [int(row[y_key]) for row in data]
    fig = go.Figure(data=go.Bar(x=x, y=y))
    fig.update_layout(title=title, margin=dict(t=50, b=30))
    return fig

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
        ])
    ])
])

@app.callback(
    [Output("top-keywords-chart", "figure"),
     Output("keywords-table", "data"),
     Output("keywords-table", "columns"),
     Output("last-updated", "children")],
    [Input("reload-button", "n_clicks")]
)
def update_dashboard(n_clicks):
    data = read_csv_dict("trendsense_keywords.csv")
    top_data = sorted(data, key=lambda x: int(x["search_volume"]), reverse=True)[:10]
    
    fig = get_bar_chart(top_data, "keyword", "search_volume", "Top 10 Keywords by Search Volume")

    columns = [{"name": col, "id": col} for col in data[0].keys()]
    
    return (
        fig,
        data,
        columns,
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=True, host="0.0.0.0", port=port)
