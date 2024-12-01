import streamlit as st
from components.composition_change import render_composition_change
from components.composition_section import render_composition_section
from components.export_section import render_export_section
from components.index_performance import render_index_performance_chart
from components.summary_metrics import render_summary_metrics_section

st.title("Stock Index Dashboard")
st.markdown("---")

render_index_performance_chart()
st.markdown("---")
render_summary_metrics_section()
st.markdown("---")
render_composition_section()
st.markdown("---")
render_composition_change()
st.markdown("---")
render_export_section()
