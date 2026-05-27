import streamlit as st

from src.ui.pages.registry import PAGE_RENDERERS


def render_sidebar() -> str:
    st.sidebar.title("Observatorio OIAP")
    st.sidebar.caption("Sistema de análisis y visualización de datos")

    return st.sidebar.radio(
        "Selecciona una sección",
        list(PAGE_RENDERERS.keys()),
    )
