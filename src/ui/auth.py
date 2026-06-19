import json

import streamlit as st
import streamlit.components.v1 as components

from src.services.auth_service import (
    SESSION_DAYS,
    AuthUser,
    authenticate_user,
    count_users,
    create_session_token,
    create_user,
    get_user_by_session_token,
    invalidate_session_token,
)

SESSION_USER_KEY = "auth_user"
AUTH_COOKIE_NAME = "oiap_session"


def current_user() -> AuthUser | None:
    data = st.session_state.get(SESSION_USER_KEY)
    if not data:
        return None
    return AuthUser(**data)


def current_user_id() -> int | None:
    user = current_user()
    return user.id if user else None


def _store_user(user: AuthUser) -> None:
    st.session_state[SESSION_USER_KEY] = {
        "id": user.id,
        "nombre": user.nombre,
        "email": user.email,
        "rol": user.rol,
    }


def _get_auth_cookie() -> str | None:
    try:
        return st.context.cookies.get(AUTH_COOKIE_NAME)
    except Exception:
        return None


def _set_auth_cookie(token: str) -> None:
    cookie_name = json.dumps(AUTH_COOKIE_NAME)
    cookie_value = json.dumps(token)
    max_age = SESSION_DAYS * 24 * 60 * 60
    components.html(
        f"""
        <script>
        document.cookie = {cookie_name} + "=" + {cookie_value} +
            "; path=/; max-age={max_age}; SameSite=Lax";
        window.parent.location.reload();
        </script>
        """,
        height=0,
    )


def _delete_auth_cookie() -> None:
    cookie_name = json.dumps(AUTH_COOKIE_NAME)
    components.html(
        f"""
        <script>
        document.cookie = {cookie_name} + "=; path=/; max-age=0; SameSite=Lax";
        window.parent.location.reload();
        </script>
        """,
        height=0,
    )


def _restore_user_from_cookie() -> bool:
    token = _get_auth_cookie()
    user = get_user_by_session_token(token)
    if not user:
        return False
    _store_user(user)
    return True


def require_login() -> bool:
    if current_user():
        return True

    if _restore_user_from_cookie():
        return True

    st.title("Observatorio OIAP")
    st.caption("Sistema de inteligencia de datos institucional")

    if count_users() == 0:
        render_first_admin_form()
    else:
        render_login_form()
    return False


def render_first_admin_form() -> None:
    st.info("Crea el primer usuario administrador para empezar a usar el sistema.")
    with st.form("first_admin_form"):
        nombre = st.text_input("Nombre")
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        remember = st.checkbox("Mantener sesion iniciada", value=True)
        submitted = st.form_submit_button("Crear administrador")

    if not submitted:
        return

    try:
        user_id = create_user(nombre, email, password, rol="admin")
        user = AuthUser(
            id=user_id,
            nombre=nombre.strip(),
            email=email.strip().lower(),
            rol="admin",
        )
        _store_user(user)
        if remember:
            _set_auth_cookie(create_session_token(user.id))
            st.stop()
        st.success("Administrador creado. Inicia sesion para continuar.")
        st.rerun()
    except Exception as error:
        st.error(f"No se pudo crear el administrador: {error}")


def render_login_form() -> None:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        remember = st.checkbox("Mantener sesion iniciada", value=True)
        submitted = st.form_submit_button("Ingresar")

    if not submitted:
        return

    user = authenticate_user(email, password)
    if not user:
        st.error("Credenciales invalidas o usuario inactivo.")
        return

    _store_user(user)
    if remember:
        _set_auth_cookie(create_session_token(user.id))
        st.stop()
    st.rerun()


def render_user_box() -> None:
    user = current_user()
    if not user:
        return

    st.sidebar.divider()
    st.sidebar.write(user.nombre)
    st.sidebar.caption(f"{user.email} · {user.rol}")

    if st.sidebar.button("Cerrar sesion"):
        invalidate_session_token(_get_auth_cookie())
        st.session_state.pop(SESSION_USER_KEY, None)
        _delete_auth_cookie()
        st.stop()


def require_role(allowed_roles: set[str]) -> bool:
    user = current_user()
    return bool(user and user.rol in allowed_roles)
