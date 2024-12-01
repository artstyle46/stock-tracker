from datetime import datetime

import requests
import streamlit as st

from config import Config


def download_file(file_url):
    response = requests.get(file_url, stream=True)
    return response.content if response.status_code == 200 else None


def render_export_section():
    st.subheader("Export Composition Data")
    target_date = st.date_input(
        "Target Date",
        value=datetime(year=2024, month=10, day=29),
        key="export_target_date",
    )

    export_option = st.selectbox(
        "Select Export Format", ["Excel", "PDF"], key="composition_select_box"
    )

    if st.button("Export", key="composition_export"):
        with st.spinner("Processing your request..."):
            if export_option == "Excel":
                file = download_file(
                    f"{Config.API_URL}/export/composition?file_type=xls&date={target_date}"
                )
                if file:
                    st.download_button(
                        "Download Excel File",
                        data=file,
                        file_name=f"composition_{target_date}.xlsx",
                        disabled=False,
                    )
                else:
                    st.error("Failed to export Excel file.")
            elif export_option == "PDF":
                file = download_file(
                    f"{Config.API_URL}/export/composition?file_type=pdf&date={target_date}"
                )
                if file:
                    st.download_button(
                        "Download PDF File",
                        data=file,
                        file_name=f"composition_{target_date}.pdf",
                        disabled=False,
                    )
                else:
                    st.error("Failed to export PDF file.")

    st.markdown("---")

    st.subheader("Export Index Performance")
    export_option = st.selectbox(
        "Select Export Format", ["Excel", "PDF"], key="index_performance_select_box"
    )

    if st.button("Export", key="index_performance_export"):
        with st.spinner("Processing your request..."):
            if export_option == "Excel":
                file = download_file(
                    f"{Config.API_URL}/export/index_performance?file_type=xls"
                )
                if file:
                    st.download_button(
                        "Download Excel File",
                        data=file,
                        file_name="index_performance.xlsx",
                        disabled=False,
                    )
                else:
                    st.error("Failed to export Excel file.")
            elif export_option == "PDF":
                file = download_file(
                    f"{Config.API_URL}/export/index_performance?file_type=pdf"
                )
                if file:
                    st.download_button(
                        "Download PDF File",
                        data=file,
                        file_name="index_performance.pdf",
                        disabled=False,
                    )
                else:
                    st.error("Failed to export PDF file.")
