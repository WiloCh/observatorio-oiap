from src.config import (
    AUDIT_LOG_TABLE,
    DECISION_TABLE,
    EVENT_TABLE,
    SCHEMA_MIGRATIONS_TABLE,
    USER_SESSION_TABLE,
    USER_TABLE,
)
from src.database.connection import get_connection, get_placeholder

CURRENT_SCHEMA_VERSION = 6
TABLE_NAME = EVENT_TABLE

EVENT_COLUMN_DEFINITIONS = {
    "fecha": "TEXT",
    "pais": "TEXT",
    "region": "TEXT",
    "programa": "TEXT",
    "tema": "TEXT",
    "tipo_fuente": "TEXT",
    "fuente": "TEXT",
    "titulo": "TEXT NOT NULL",
    "descripcion": "TEXT",
    "nivel_riesgo": "TEXT",
    "nivel_oportunidad": "TEXT",
    "relevancia": "INTEGER DEFAULT 0 CHECK (relevancia BETWEEN 0 AND 5)",
    "decision_impacto": "TEXT",
    "accion_recomendada": "TEXT",
    "derivacion": "TEXT",
    "estado_seguimiento": "TEXT DEFAULT 'Detectado'",
    "observaciones": "TEXT",
}

USER_COLUMN_DEFINITIONS = {
    "nombre": "TEXT NOT NULL DEFAULT ''",
    "email": "TEXT",
    "rol": "TEXT NOT NULL DEFAULT 'analista'",
    "password_hash": "TEXT",
    "activo": "INTEGER NOT NULL DEFAULT 1",
}


def create_table() -> None:
    with get_connection() as conn:
        create_users_table(conn)
        create_user_sessions_table(conn)
        create_events_table(conn)
        create_decisions_table(conn)
        create_audit_log_table(conn)
        create_schema_migrations_table(conn)
        migrate_missing_user_columns(conn)
        migrate_missing_event_columns(conn)
        insert_schema_version(conn)
        create_indexes(conn)
        conn.commit()


def create_users_table(conn) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {USER_TABLE} (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            rol TEXT NOT NULL DEFAULT 'analista',
            password_hash TEXT,
            activo INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def create_user_sessions_table(conn) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {USER_SESSION_TABLE} (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMPTZ NOT NULL,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES {USER_TABLE}(id)
        )
        """
    )


def create_events_table(conn) -> None:
    column_sql = ",\n        ".join(
        f"{column} {definition}"
        for column, definition in EVENT_COLUMN_DEFINITIONS.items()
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {EVENT_TABLE} (
            id SERIAL PRIMARY KEY,
            {column_sql},
            creado_por INTEGER,
            actualizado_por INTEGER,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ,
            FOREIGN KEY (creado_por) REFERENCES {USER_TABLE}(id),
            FOREIGN KEY (actualizado_por) REFERENCES {USER_TABLE}(id)
        )
        """
    )


def create_decisions_table(conn) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {DECISION_TABLE} (
            id SERIAL PRIMARY KEY,
            evento_id INTEGER NOT NULL,
            decision TEXT NOT NULL,
            accion_tomada TEXT,
            responsable TEXT,
            estado TEXT NOT NULL DEFAULT 'Registrada',
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (evento_id) REFERENCES {EVENT_TABLE}(id)
        )
        """
    )


def create_audit_log_table(conn) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {AUDIT_LOG_TABLE} (
            id SERIAL PRIMARY KEY,
            tabla TEXT NOT NULL,
            registro_id INTEGER,
            accion TEXT NOT NULL,
            usuario_id INTEGER,
            detalle TEXT,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES {USER_TABLE}(id)
        )
        """
    )


def create_schema_migrations_table(conn) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA_MIGRATIONS_TABLE} (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def migrate_missing_user_columns(conn) -> None:
    existing_columns = get_table_columns(conn, USER_TABLE)
    for column, definition in USER_COLUMN_DEFINITIONS.items():
        if column not in existing_columns:
            conn.execute(f"ALTER TABLE {USER_TABLE} ADD COLUMN {column} {definition}")


def migrate_missing_event_columns(conn) -> None:
    existing_columns = get_table_columns(conn, EVENT_TABLE)
    extra_columns = {
        **EVENT_COLUMN_DEFINITIONS,
        "creado_por": "INTEGER",
        "actualizado_por": "INTEGER",
        "updated_at": "TIMESTAMPTZ",
    }

    for column, definition in extra_columns.items():
        if column not in existing_columns:
            conn.execute(f"ALTER TABLE {EVENT_TABLE} ADD COLUMN {column} {definition}")


def get_table_columns(conn, table_name: str) -> set[str]:
    rows = conn.execute(
        f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = {get_placeholder()}
        """,
        (table_name,),
    ).fetchall()
    return {row[0] for row in rows}


def insert_schema_version(conn) -> None:
    conn.execute(
        f"INSERT INTO {SCHEMA_MIGRATIONS_TABLE} (version) VALUES ({get_placeholder()}) ON CONFLICT (version) DO NOTHING",
        (CURRENT_SCHEMA_VERSION,),
    )


def create_indexes(conn) -> None:
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_eventos_fecha ON {EVENT_TABLE} (fecha)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_eventos_pais ON {EVENT_TABLE} (pais)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_eventos_programa ON {EVENT_TABLE} (programa)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_eventos_estado ON {EVENT_TABLE} (estado_seguimiento)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_decisiones_evento ON {DECISION_TABLE} (evento_id)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_audit_log_tabla_registro ON {AUDIT_LOG_TABLE} (tabla, registro_id)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_sesiones_usuario_token ON {USER_SESSION_TABLE} (token_hash)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_sesiones_usuario_expira ON {USER_SESSION_TABLE} (expires_at)")
