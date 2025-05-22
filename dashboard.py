import os
import csv
from dash import Dash, dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import dash_vega_lite as dvl
from pathlib import Path
from datetime import datetime

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="TrendSense Dashboard")

BASE_PATH = Path("generated_data")

def read_csv_dict(filename):
    with open(BASE_PATH / filename, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def generate_vega_lite_bar(data, x_key, y_key, title):
    # Vega-Lite spec for a simple bar chart
    spec = {
        "data": {"values": data},
        "mark": "bar",
        "encoding": {
            "x": {
                "field": x_key,
                "type": "nominal",
                "axis": {"labelAngle": -45, "labelOverlap": "parity"}
            },
            "y": {
                "field": y_key,
                "type": "quantitative"
            }
        },
        "title": title,
        "width": "container",
        "height": 300,
        "autosize": {"type": "fit", "contains": "padding"}
    }
    return spec

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
            dvl.VegaLite(id="top-keywords-chart", spec={}, style={"height": "50vh"}),
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
    [Output("top-keywords-chart", "spec"),
     Output("keywords-table", "data"),
     Output("keywords-table", "columns"),
     Output("last-updated", "children")],
    [Input("reload-button", "n_clicks")]
)
def update_dashboard(n_clicks):
    data = read_csv_dict("trendsense_keywords.csv")
    # Sort top 10 by search_volume as int
    top_data = sorted(data, key=lambda x: int(x["search_volume"]), reverse=True)[:10]

    # Vega-Lite spec for bar chart
    spec = generate_vega_lite_bar(top_data, "keyword", "search_volume", "Top 10 Keywords by Search Volume")

    columns = [{"name": col, "id": col} for col in data[0].keys()]

    return (
        spec,
        data,
        columns,
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=True, host="0.0.0.0", port=port)
