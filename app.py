import os
import csv
from dash import Dash, dcc, html, dash_table, Input, Output
import plotly.graph_objects as go
from datetime import datetime
from flask import Flask

# Initialize minimal Flask app
server = Flask(__name__)

# Initialize Dash app with minimal configuration
app = Dash(__name__, server=server, title="TrendSense Dashboard")

def read_csv_dict(filename):
    """Read CSV file into list of dictionaries without pandas"""
    with open(f"generated_data/{filename}", newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def get_bar_chart(data, x_key, y_key, title):
    """Create bar chart using graph_objects only"""
    x = [row[x_key] for row in data]
    y = [int(row[y_key]) for row in data]
    
    fig = go.Figure(data=go.Bar(
        x=x,
        y=y,
        marker_color='#4F46E5',
        opacity=0.8
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=50, b=30, l=40, r=40),
        height=400
    )
    
    return fig

def get_line_chart(data, x_key, y_key, color_key, title):
    """Create line chart using graph_objects only"""
    fig = go.Figure()
    
    # Group data by color_key (keyword)
    keywords = {row[color_key] for row in data}
    colors = ['#4F46E5', '#10B981', '#F59E0B']  # Predefined colors
    
    for i, keyword in enumerate(keywords):
        filtered = [row for row in data if row[color_key] == keyword]
        x = [row[x_key] for row in filtered]
        y = [int(row[y_key]) for row in filtered]
        
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            name=keyword,
            line=dict(color=colors[i % len(colors)], width=2),
            mode='lines+markers'
        ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=50, b=30, l=40, r=40),
        height=400,
        hovermode='x unified'
    )
    
    return fig

# Minimal layout with inline styles
app.layout = html.Div([
    html.Div([
        html.H2("📊 TrendSense Dashboard", style={
            'color': '#1F2937',
            'marginBottom': '10px'
        }),
        html.Div(id="last-updated", style={
            'color': '#6B7280',
            'textAlign': 'right',
            'fontSize': '0.9rem'
        })
    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'marginBottom': '20px',
        'padding': '0 20px'
    }),
    
    html.Button("🔄 Reload Data", id="reload-button", style={
        'background': '#4F46E5',
        'color': 'white',
        'border': 'none',
        'padding': '8px 16px',
        'borderRadius': '6px',
        'cursor': 'pointer',
        'marginBottom': '20px',
        'marginLeft': '20px'
    }),
    
    dcc.Tabs([
        dcc.Tab(label="Top Keywords", children=[
            dcc.Graph(id="top-keywords-chart", config={"displayModeBar": False}),
            dash_table.DataTable(
                id="keywords-table",
                page_size=10,
                style_table={
                    'overflowX': 'auto',
                    'border': '1px solid #E5E7EB',
                    'borderRadius': '6px',
                    'margin': '20px',
                    'maxWidth': '95vw'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'border': '1px solid #E5E7EB'
                },
                style_header={
                    'backgroundColor': '#F3F4F6',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[{
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#F9FAFB'
                }]
            )
        ]),
        
        dcc.Tab(label="Search Trends", children=[
            dcc.Graph(id="search-trend-chart", config={"displayModeBar": False})
        ])
    ])
])

@app.callback(
    [Output("top-keywords-chart", "figure"),
     Output("search-trend-chart", "figure"),
     Output("keywords-table", "data"),
     Output("keywords-table", "columns"),
     Output("last-updated", "children")],
    [Input("reload-button", "n_clicks")]
)
def update_dashboard(n_clicks):
    # Load data without pandas
    keywords_data = read_csv_dict("trendsense_keywords.csv")
    trends_data = read_csv_dict("trendsense_search_trends.csv")
    
    # Process top keywords
    top_keywords = sorted(keywords_data, key=lambda x: int(x["search_volume"]), reverse=True)[:10]
    keywords_fig = get_bar_chart(top_keywords, "keyword", "search_volume", "Top 10 Keywords by Search Volume")
    
    # Process search trends
    top_3_keywords = [row["keyword"] for row in top_keywords[:3]]
    filtered_trends = [row for row in trends_data if row["keyword"] in top_3_keywords]
    trends_fig = get_line_chart(filtered_trends, "date", "search_volume", "keyword", "Search Trends for Top 3 Keywords")
    
    # Prepare table data
    columns = [{"name": col, "id": col} for col in keywords_data[0].keys()]
    
    return (
        keywords_fig,
        trends_fig,
        keywords_data,
        columns,
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

@server.route('/')
def serve_dash_app():
    return app.index()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=True, host="0.0.0.0", port=port)
