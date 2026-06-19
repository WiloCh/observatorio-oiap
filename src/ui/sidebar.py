import streamlit as st

from src.ui.auth import render_user_box
from src.ui.pages.registry import NAVIGATION_GROUPS


def render_sidebar() -> str:
    st.sidebar.title("Observatorio OIAP")
    st.sidebar.caption("Sistema de analisis y visualizacion de datos")

    page_options = []
    for group_label, pages in NAVIGATION_GROUPS.items():
        st.sidebar.markdown(f"**{group_label}**")
        page_options.extend(pages)

    selected = st.sidebar.radio(
        "Selecciona una seccion",
        page_options,
    )

    render_user_box()
    return selected
