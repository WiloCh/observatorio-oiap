import pandas as pd
import streamlit as st

from src.config import USER_TABLE
from src.database.audit_repository import log_action
from src.domain.constants import USER_ROLES
from src.services.auth_service import create_user, list_users, set_user_active
from src.ui.auth import current_user, require_role


def render_users_page() -> None:
    st.title("Usuarios y roles")

    if not require_role({"admin"}):
        st.warning("Solo un usuario administrador puede gestionar usuarios.")
        return

    st.subheader("Crear usuario")
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre")
        email = col2.text_input("Email")
        col3, col4 = st.columns(2)
        rol = col3.selectbox("Rol", USER_ROLES, index=USER_ROLES.index("analista"))
        password = col4.text_input("Contraseña inicial", type="password")
        submitted = st.form_submit_button("Crear usuario")

    if submitted:
        try:
            user_id = create_user(nombre, email, password, rol)
            actor = current_user()
            log_action(
                tabla=USER_TABLE,
                registro_id=user_id,
                accion="create_user",
                usuario_id=actor.id if actor else None,
                detalle=f"Usuario creado: {email.strip().lower()} ({rol})",
            )
            st.success("Usuario creado correctamente.")
        except Exception as error:
            st.error(f"No se pudo crear el usuario: {error}")

    st.subheader("Usuarios registrados")
    users = list_users()
    if not users:
        st.info("No hay usuarios registrados.")
        return

    st.dataframe(pd.DataFrame(users), width="stretch", hide_index=True)

    st.subheader("Activar o desactivar")
    options = {f"{user['nombre']} · {user['email']} · {user['rol']}": user for user in users}
    selected_label = st.selectbox("Usuario", list(options.keys()))
    selected_user = options[selected_label]
    active = st.toggle("Activo", value=selected_user["activo"])

    if st.button("Actualizar estado"):
        set_user_active(selected_user["id"], active)
        actor = current_user()
        log_action(
            tabla=USER_TABLE,
            registro_id=selected_user["id"],
            accion="set_user_active",
            usuario_id=actor.id if actor else None,
            detalle=f"activo={active}",
        )
        st.success("Estado actualizado.")
        st.rerun()
