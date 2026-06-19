import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.config import USER_SESSION_TABLE, USER_TABLE
from src.database.connection import get_connection, get_placeholder, placeholders
from src.domain.constants import USER_ROLES

PBKDF2_ITERATIONS = 120_000
SESSION_DAYS = 7


@dataclass(frozen=True)
class AuthUser:
    id: int
    nombre: str
    email: str
    rol: str


def hash_password(password: str, salt: bytes | None = None) -> str:
    if not password:
        raise ValueError("La contraseña no puede estar vacía.")
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str | None) -> bool:
    if not password or not stored_hash:
        return False
    try:
        algorithm, iterations, salt_hex, digest_hex = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except ValueError:
        return False


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def count_users() -> int:
    with get_connection() as conn:
        row = conn.execute(f"SELECT COUNT(*) FROM {USER_TABLE}").fetchone()
    return int(row[0])


def create_user(nombre: str, email: str, password: str, rol: str = "analista") -> int:
    nombre = nombre.strip()
    email = email.strip().lower()
    if not nombre:
        raise ValueError("El nombre es obligatorio.")
    if not email:
        raise ValueError("El email es obligatorio.")
    if rol not in USER_ROLES:
        raise ValueError(f"Rol inválido: {rol}")

    password_hash = hash_password(password)
    params = (nombre, email, rol, password_hash)
    query = (
        f"INSERT INTO {USER_TABLE} (nombre, email, rol, password_hash) "
        f"VALUES ({placeholders(len(params))})"
    )
    with get_connection() as conn:
        cursor = conn.execute(query, params)
        conn.commit()
        if hasattr(cursor, "lastrowid") and cursor.lastrowid:
            return int(cursor.lastrowid)

        row = conn.execute(
            f"SELECT id FROM {USER_TABLE} WHERE email = {get_placeholder()}",
            (email,),
        ).fetchone()
        return int(row[0])


def authenticate_user(email: str, password: str) -> AuthUser | None:
    query = (
        "SELECT id, nombre, email, rol, password_hash "
        f"FROM {USER_TABLE} WHERE email = {get_placeholder()} AND activo = 1"
    )
    with get_connection() as conn:
        row = conn.execute(query, (email.strip().lower(),)).fetchone()

    if not row or not verify_password(password, row[4]):
        return None
    return AuthUser(id=int(row[0]), nombre=row[1], email=row[2], rol=row[3])


def get_user_by_email(email: str) -> AuthUser | None:
    query = (
        "SELECT id, nombre, email, rol "
        f"FROM {USER_TABLE} WHERE email = {get_placeholder()} AND activo = 1"
    )
    with get_connection() as conn:
        row = conn.execute(query, (email.strip().lower(),)).fetchone()
    if not row:
        return None
    return AuthUser(id=int(row[0]), nombre=row[1], email=row[2], rol=row[3])


def create_session_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    token_hash = hash_session_token(token)
    with get_connection() as conn:
        conn.execute(
            f"DELETE FROM {USER_SESSION_TABLE} WHERE expires_at <= CURRENT_TIMESTAMP"
        )
        conn.execute(
            f"""
            INSERT INTO {USER_SESSION_TABLE} (usuario_id, token_hash, expires_at)
            VALUES ({placeholders(3)})
            """,
            (user_id, token_hash, expires_at),
        )
        conn.commit()
    return token


def get_user_by_session_token(token: str | None) -> AuthUser | None:
    if not token:
        return None

    token_hash = hash_session_token(token)
    placeholder = get_placeholder()
    query = f"""
        SELECT u.id, u.nombre, u.email, u.rol
        FROM {USER_SESSION_TABLE} s
        JOIN {USER_TABLE} u ON u.id = s.usuario_id
        WHERE s.token_hash = {placeholder}
          AND s.expires_at > CURRENT_TIMESTAMP
          AND u.activo = 1
    """
    with get_connection() as conn:
        row = conn.execute(query, (token_hash,)).fetchone()

    if not row:
        return None
    return AuthUser(id=int(row[0]), nombre=row[1], email=row[2], rol=row[3])


def invalidate_session_token(token: str | None) -> None:
    if not token:
        return
    with get_connection() as conn:
        conn.execute(
            f"DELETE FROM {USER_SESSION_TABLE} WHERE token_hash = {get_placeholder()}",
            (hash_session_token(token),),
        )
        conn.commit()


def list_users() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT id, nombre, email, rol, activo, created_at FROM {USER_TABLE} ORDER BY id"
        ).fetchall()
    return [
        {
            "id": int(row[0]),
            "nombre": row[1],
            "email": row[2],
            "rol": row[3],
            "activo": bool(row[4]),
            "created_at": row[5],
        }
        for row in rows
    ]


def set_user_active(user_id: int, active: bool) -> None:
    placeholder = get_placeholder()
    with get_connection() as conn:
        conn.execute(
            f"UPDATE {USER_TABLE} SET activo = {placeholder} WHERE id = {placeholder}",
            (1 if active else 0, user_id),
        )
        conn.commit()
