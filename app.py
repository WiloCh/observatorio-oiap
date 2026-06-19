import streamlit as st

from src.config import APP_NAME
from src.database.schema import create_table
from src.ui.auth import require_login
from src.ui.pages.registry import PAGE_RENDERERS
from src.ui.sidebar import render_sidebar
from src.ui.theme import apply_app_theme

st.set_page_config(
    page_title=f"{APP_NAME} - Observatorio",
    layout="wide",
)

apply_app_theme()
create_table()

if require_login():
    selected_page = render_sidebar()
    PAGE_RENDERERS[selected_page]()
