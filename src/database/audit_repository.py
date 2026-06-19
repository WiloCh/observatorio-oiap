from src.config import AUDIT_LOG_TABLE
from src.database.connection import get_connection, get_placeholder, placeholders


def log_action(
    tabla: str,
    accion: str,
    registro_id: int | None = None,
    usuario_id: int | None = None,
    detalle: str = "",
    conn=None,
) -> None:
    params = (tabla, registro_id, accion, usuario_id, detalle)
    query = (
        f"INSERT INTO {AUDIT_LOG_TABLE} (tabla, registro_id, accion, usuario_id, detalle) "
        f"VALUES ({placeholders(len(params))})"
    )

    if conn is not None:
        conn.execute(query, params)
        return

    with get_connection() as connection:
        connection.execute(query, params)
        connection.commit()


def get_audit_log(limit: int = 100) -> list[tuple]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT tabla, registro_id, accion, usuario_id, detalle, created_at "
            f"FROM {AUDIT_LOG_TABLE} ORDER BY id DESC LIMIT {get_placeholder()}",
            (limit,),
        ).fetchall()
