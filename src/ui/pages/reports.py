import streamlit as st

from src.database.repository import get_all_data
from src.services.analysis_service import enrich_dataframe, get_decision_queue, get_executive_kpis


def render_reports_page() -> None:
    st.title("Reportes")
    st.caption("Exporta información para revisión ejecutiva o respaldo institucional.")

    raw_df = get_all_data()
    if raw_df.empty:
        st.info("No hay datos disponibles para reportar.")
        return

    df = enrich_dataframe(raw_df)
    kpis = get_executive_kpis(df)
    queue = get_decision_queue(df, top_n=20)

    st.subheader("Resumen ejecutivo")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros", kpis["total_registros"])
    c2.metric("Críticas", kpis["alertas_criticas"])
    c3.metric("Pendientes", kpis["pendientes_de_accion"])
    c4.metric("Usados", kpis["usados_en_decision"])

    st.download_button(
        "Descargar base completa CSV",
        data=df.to_csv(index=False),
        file_name="observatorio_oiap_reporte_completo.csv",
        mime="text/csv",
    )

    if not queue.empty:
        st.download_button(
            "Descargar cola de decisión CSV",
            data=queue.to_csv(index=False),
            file_name="observatorio_oiap_cola_decision.csv",
            mime="text/csv",
        )
        st.dataframe(queue, width="stretch", hide_index=True)
