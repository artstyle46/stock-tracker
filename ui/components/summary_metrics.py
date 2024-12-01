from datetime import datetime

import requests
import streamlit as st

from config import Config


def fetch_summary_metrics(start_date, end_date):
    response = requests.get(
        f"{Config.API_URL}/indexes/summary",
        params={"start_date": start_date, "end_date": end_date},
    )
    return response.json() if response.status_code == 200 else {}


def render_summary_metrics_section():
    st.subheader("Summary Metrics")
    start_date = st.date_input(
        "Start Date",
        value=datetime(year=2024, month=9, day=29),
        key="summary_start_date",
    )
    end_date = st.date_input(
        "End Date", value=datetime(year=2024, month=10, day=29), key="summary_end_date"
    )

    if start_date <= end_date:
        summary_metrics = fetch_summary_metrics(
            start_date=start_date.isoformat(), end_date=end_date.isoformat()
        )
        if summary_metrics:
            col1, col2 = st.columns(2)
            col1.metric(
                "Cumulative Return (%)", f"{summary_metrics['cumulative_return']:.2f}"
            )
            col2.metric(
                "Avg Daily Change (%)", f"{summary_metrics['average_daily_change']:.2f}"
            )
            st.write("Composition Changes")
            st.line_chart(summary_metrics.get("composition_changes", []))

            st.write("Daily Percentage Changes")
            st.line_chart(summary_metrics.get("daily_changes", []))
    else:
        st.error("Start Date must be before or equal to End Date.")
