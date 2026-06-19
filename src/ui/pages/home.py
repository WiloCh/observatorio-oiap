import io

import streamlit as st

from src.domain.constants import OBSERVATORY_DECISION_QUESTION
from src.services.cleaning_service import generate_template


def render_home_page() -> None:
    st.title("Sistema de inteligencia de datos del Observatorio")
    st.caption("OIAP / IIAP")

    st.markdown(
        f"""
        El sistema ordena hallazgos institucionales para que puedan ser analizados,
        priorizados y usados en decisiones estrategicas reales.

        **Criterio central:** {OBSERVATORY_DECISION_QUESTION}

        - El Observatorio monitorea, analiza, anticipa y emite alertas.
        - El Think Tank puede traducir evidencia en propuestas.
        - El Circulo Operativo decide viabilidad, activacion y seguimiento.
        """
    )

    st.subheader("Plantilla base")
    template_df = generate_template()
    st.dataframe(template_df, width="stretch")

    csv_buffer = io.StringIO()
    template_df.to_csv(csv_buffer, index=False)

    st.download_button(
        label="Descargar plantilla CSV",
        data=csv_buffer.getvalue(),
        file_name="plantilla_observatorio_oiap.csv",
        mime="text/csv",
    )
