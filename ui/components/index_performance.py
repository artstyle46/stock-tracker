from datetime import date, datetime

import pandas as pd
import requests
import streamlit as st

from config import Config


def fetch_index_performance(start_date: date, end_date: date):
    response = requests.get(
        f"{Config.API_URL}/indexes/performance",
        params={"start_date": start_date, "end_date": end_date},
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch index performance data.")
        return []


def render_index_performance_chart():
    st.title("Index Performance Over a period")
    start_date = st.date_input(
        "Start Date", value=datetime(year=2024, month=9, day=29), key="ipc_start_date"
    )
    end_date = st.date_input(
        "End Date", value=datetime(year=2024, month=10, day=29), key="ipc_end_date"
    )
    data = fetch_index_performance(start_date, end_date)

    if data:
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        st.line_chart(
            df.set_index("date")["index_value"], use_container_width=True, height=400
        )
    else:
        st.warning("No data available for the chart.")
