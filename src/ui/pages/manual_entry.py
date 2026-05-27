from datetime import datetime

import pandas as pd
import streamlit as st

from src.database.repository import insert_dataframe
from src.domain.constants import (
    DERIVATION_TARGETS,
    FOLLOW_UP_STATUSES,
    LEVELS,
    PROGRAMS,
    RELEVANCE_RANGE,
    SOURCE_TYPES,
)
from src.services.cleaning_service import clean_dataframe


def render_manual_entry_page() -> None:
    st.title("Registro manual")
    st.caption("Registra hallazgos que puedan alimentar decisiones, alertas o seguimiento institucional.")

    with st.form("manual_form"):
        st.subheader("Identificación del hallazgo")
        col1, col2, col3 = st.columns(3)
        fecha = col1.date_input("Fecha", value=datetime.today())
        pais = col2.text_input("País")
        region = col3.text_input("Región")

        col4, col5, col6 = st.columns(3)
        programa = col4.selectbox("Programa del Observatorio", PROGRAMS)
        tema = col5.text_input("Tema")
        tipo_fuente = col6.selectbox("Tipo de fuente", SOURCE_TYPES)

        fuente = st.text_input("Fuente")
        titulo = st.text_input("Título")
        descripcion = st.text_area("Descripción del hallazgo")

        st.subheader("Lectura estratégica")
        col7, col8, col9 = st.columns(3)
        nivel_riesgo = col7.selectbox("Nivel de riesgo", LEVELS)
        nivel_oportunidad = col8.selectbox("Nivel de oportunidad", LEVELS)
        relevancia = col9.slider(
            "Relevancia para decisión",
            min_value=RELEVANCE_RANGE.minimum,
            max_value=RELEVANCE_RANGE.maximum,
            value=3,
        )

        decision_impacto = st.text_area(
            "¿A qué decisión concreta alimenta esto?",
            placeholder="Ejemplo: priorizar una reunión, elevar una alerta, preparar propuesta, sostener monitoreo.",
        )
        accion_recomendada = st.text_area(
            "Acción recomendada",
            placeholder="Ejemplo: elevar al Think Tank, preparar benchmark, validar con Círculo Operativo.",
        )

        col10, col11 = st.columns(2)
        derivacion = col10.selectbox("Derivar a", DERIVATION_TARGETS)
        estado_seguimiento = col11.selectbox("Estado de seguimiento", FOLLOW_UP_STATUSES)

        observaciones = st.text_area("Observaciones internas")
        submitted = st.form_submit_button("Guardar hallazgo")

    if not submitted:
        return

    manual_df = pd.DataFrame(
        [
            {
                "fecha": fecha,
                "pais": pais,
                "region": region,
                "programa": programa,
                "tema": tema,
                "tipo_fuente": tipo_fuente,
                "fuente": fuente,
                "titulo": titulo,
                "descripcion": descripcion,
                "nivel_riesgo": nivel_riesgo,
                "nivel_oportunidad": nivel_oportunidad,
                "relevancia": relevancia,
                "decision_impacto": decision_impacto,
                "accion_recomendada": accion_recomendada,
                "derivacion": derivacion,
                "estado_seguimiento": estado_seguimiento,
                "observaciones": observaciones,
            }
        ]
    )

    clean_df = clean_dataframe(manual_df)
    inserted = insert_dataframe(clean_df)

    if inserted > 0:
        st.success("Hallazgo guardado correctamente.")
    else:
        st.warning("No se guardó el hallazgo. Verifica que tenga título y lectura estratégica suficiente.")
