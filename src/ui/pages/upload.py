import streamlit as st

from src.database.repository import insert_dataframe
from src.services.cleaning_service import clean_dataframe
from src.services.ingestion_service import read_uploaded_file


def render_upload_page() -> None:
    st.title("Carga masiva de hallazgos")
    st.caption("Los archivos pueden venir incompletos: el sistema completa columnas nuevas y normaliza valores.")

    uploaded_file = st.file_uploader(
        "Sube un archivo CSV o Excel",
        type=["csv", "xlsx", "xls"],
    )

    if uploaded_file is None:
        return

    try:
        raw_df = read_uploaded_file(uploaded_file)

        st.subheader("Vista previa original")
        st.dataframe(raw_df.head(10), width="stretch")

        clean_df = clean_dataframe(raw_df)

        st.subheader("Vista previa normalizada")
        st.dataframe(clean_df.head(10), width="stretch")

        actionable = clean_df[
            clean_df["decision_impacto"].astype(str).str.strip().ne("")
            | clean_df["accion_recomendada"].astype(str).str.strip().ne("")
        ]
        st.info(f"{len(actionable)} de {len(clean_df)} registros incluyen decisión o acción recomendada.")

        if st.button("Guardar hallazgos en la base"):
            inserted = insert_dataframe(clean_df)
            st.success(f"Se guardaron {inserted} registros.")
    except Exception as error:
        st.error(f"Error al procesar el archivo: {error}")
