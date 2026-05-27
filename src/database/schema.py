from src.database.connection import get_connection
from src.domain.constants import EVENT_TABLE

CURRENT_SCHEMA_VERSION = 2
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


def create_table() -> None:
    column_sql = ",\n        ".join(
        f"{column} {definition}"
        for column, definition in EVENT_COLUMN_DEFINITIONS.items()
    )
    query = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {column_sql},
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """

    with get_connection() as conn:
        conn.execute(query)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        migrate_missing_columns(conn)
        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
            (CURRENT_SCHEMA_VERSION,),
        )
        conn.commit()


def migrate_missing_columns(conn) -> None:
    existing_columns = {
        row[1] for row in conn.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall()
    }

    for column, definition in EVENT_COLUMN_DEFINITIONS.items():
        if column not in existing_columns:
            conn.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN {column} {definition}")
