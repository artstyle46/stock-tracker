from datetime import datetime

import pandas as pd
import requests
import streamlit as st

from config import Config


def fetch_composition_change(start_date, end_date):
    response = requests.get(
        f"{Config.API_URL}/indexes/composition_change",
        params={"start_date": start_date, "end_date": end_date},
    )
    return response.json() if response.status_code == 200 else []


def render_composition_change():
    st.subheader("Composition Changes")
    start_date = st.date_input(
        "Start Date",
        value=datetime(year=2024, month=11, day=2),
        key="comp_change_start_date",
    )
    end_date = st.date_input(
        "End Date",
        value=datetime(year=2024, month=12, day=2),
        key="comp_change_end_date",
    )
    composition_data = fetch_composition_change(start_date, end_date)
    df_changes = pd.DataFrame(
        [
            {"date": date, "composition_change": "Yes" if changed else "No"}
            for date, changed in composition_data.items()
        ]
    )
    st.write("Table of Dates with Composition Changes")
    st.dataframe(df_changes)

    st.write("Days with Composition Changes")
    changed_dates = [date for date, changed in composition_data.items() if changed]
    st.markdown("\n".join([f"- **{date}**" for date in changed_dates]))
