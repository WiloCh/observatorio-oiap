import streamlit as st

from src.database.repository import get_all_data
from src.services.analysis_service import enrich_dataframe, get_decision_queue


def render_alerts_page() -> None:
    st.title("Alertas")
    st.caption("Hallazgos que requieren revisión, derivación o decisión institucional.")

    raw_df = get_all_data()
    if raw_df.empty:
        st.info("No hay hallazgos cargados.")
        return

    df = enrich_dataframe(raw_df)
    critical = df[df["clasificacion_alerta"].isin(["Crítica", "Alta"])]
    pending = critical[~critical["estado_seguimiento"].isin(["Usado en decisión", "Descartado"])]

    c1, c2, c3 = st.columns(3)
    c1.metric("Alertas abiertas", len(pending))
    c2.metric("Críticas", len(df[df["clasificacion_alerta"] == "Crítica"]))
    c3.metric("Alta prioridad", len(df[df["prioridad"] >= 8]))

    st.subheader("Cola prioritaria")
    queue = get_decision_queue(df, top_n=15)
    if queue.empty:
        st.info("No hay alertas accionables en este momento.")
        return

    st.dataframe(queue, width="stretch", hide_index=True)
