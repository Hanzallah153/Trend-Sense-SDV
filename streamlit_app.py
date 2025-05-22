import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime

# Page config
st.set_page_config(page_title="TrendSense Dashboard", layout="wide")
st.title("📊 TrendSense: AI-Powered Market Trend Dashboard")

# Load data
BASE_PATH = Path("generated_data")

@st.cache_data
def load_data():
    return {
        "keywords": pd.read_csv(BASE_PATH / "trendsense_keywords.csv"),
        "consumer": pd.read_csv(BASE_PATH / "trendsense_consumer_behavior.csv"),
        "search_trends": pd.read_csv(BASE_PATH / "trendsense_search_trends.csv"),
        "predictions": pd.read_csv(BASE_PATH / "trendsense_market_predictions.csv"),
        "sales": pd.read_csv(BASE_PATH / "trendsense_sales_correlation.csv")
    }

data = load_data()
st.markdown(f"#### Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Tabs
tabs = st.tabs(["Top Keywords", "Search Trends Over Time", "Market Predictions", "Sales Correlation", "Raw Data"])

# Tab 1: Top Keywords
with tabs[0]:
    st.subheader("Top 10 Keywords by Search Volume")
    top_keywords_df = data["keywords"].sort_values("search_volume", ascending=False).head(10)
    fig = px.bar(top_keywords_df, x="keyword", y="search_volume", color="category")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(data["keywords"], use_container_width=True)

# Tab 2: Search Trends
with tabs[1]:
    st.subheader("Search Volume Trends for Top 5 Keywords")
    top_5 = data["keywords"].sort_values("search_volume", ascending=False).head(5)["keyword"].tolist()
    filtered_trends = data["search_trends"][data["search_trends"]["keyword"].isin(top_5)]
    fig = px.line(filtered_trends, x="date", y="search_volume", color="keyword")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(data["search_trends"], use_container_width=True)

# Tab 3: Market Predictions
with tabs[2]:
    st.subheader("Market Predictions: 30-day vs 90-day Interest")
    fig = px.scatter(
        data["predictions"], x="predicted_interest_30d", y="predicted_interest_90d",
        size="confidence_score", color="category", hover_name="keyword"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(data["predictions"], use_container_width=True)

# Tab 4: Sales Correlation
with tabs[3]:
    st.subheader("Sales Volume vs Search Volume with Conversion Rate")
    fig = px.scatter(
        data["sales"], x="search_volume", y="sales_volume",
        size="conversion_rate", color="revenue"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(data["sales"], use_container_width=True)

# Tab 5: Raw Data
with tabs[4]:
    st.subheader("Raw Keywords Data")
    st.dataframe(data["keywords"], use_container_width=True)
