import streamlit as st

from src.database.schema import create_table
from src.ui.pages.registry import PAGE_RENDERERS
from src.ui.sidebar import render_sidebar

st.set_page_config(
    page_title="OIAP - Observatorio",
    layout="wide",
)

create_table()

selected_page = render_sidebar()
PAGE_RENDERERS[selected_page]()

