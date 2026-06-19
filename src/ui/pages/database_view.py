import streamlit as st

from src.database.repository import delete_all_data, get_all_data
from src.ui.auth import current_user_id, require_role


DELETE_CONFIRMATION = "ELIMINAR"


def render_database_view_page() -> None:
    st.title("Base de datos")

    df = get_all_data()
    st.dataframe(df, width="stretch")
    st.write(f"Total de registros: {len(df)}")

    if not df.empty:
        st.download_button(
            label="Descargar respaldo CSV",
            data=df.to_csv(index=False),
            file_name="respaldo_observatorio_oiap.csv",
            mime="text/csv",
        )

    st.divider()
    st.subheader("Zona de mantenimiento")

    if not require_role({"admin", "direccion"}):
        st.info("Solo admin o dirección pueden eliminar registros.")
        return

    confirmation = st.text_input(
        f"Escribe {DELETE_CONFIRMATION} para habilitar el borrado total"
    )

    if st.button("Eliminar todos los datos", disabled=confirmation != DELETE_CONFIRMATION):
        delete_all_data(usuario_id=current_user_id())
        st.success("Se eliminaron todos los registros.")
