from datetime import datetime

import pandas as pd
import requests
import streamlit as st

from config import Config


def fetch_composition(date):
    response = requests.get(
        f"{Config.API_URL}/indexes/composition", params={"target_date": date}
    )
    return response.json()["data"] if response.status_code == 200 else []


def render_composition_section():
    st.subheader("Index Composition")
    selected_date = st.date_input(
        "Select a Date", value=datetime(year=2024, month=10, day=29)
    )
    composition_data = fetch_composition(selected_date.isoformat())
    if composition_data:
        df_composition = pd.DataFrame(composition_data)
        st.write("Top 5 Stocks by Market Cap (Bar Chart)")
        st.bar_chart(df_composition.set_index("ticker")["market_cap"])
        st.write("Full Composition (Table)")
        st.dataframe(df_composition)
