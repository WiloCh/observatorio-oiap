import pandas as pd

from src.database.audit_repository import log_action
from src.database.connection import get_connection, placeholders, transaction
from src.database.schema import TABLE_NAME
from src.domain.constants import EVENT_COLUMNS, EVENT_READ_COLUMNS
from src.domain.models import EventRecord


def validate_event_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [column for column in EVENT_COLUMNS if column not in df.columns]
    if missing_columns:
        columns = ", ".join(missing_columns)
        raise ValueError(f"Faltan columnas requeridas: {columns}")

    normalized = df[EVENT_COLUMNS].copy()
    for record in normalized.to_dict(orient="records"):
        EventRecord.from_mapping(record).validate()
    return normalized


def insert_dataframe(df: pd.DataFrame, usuario_id: int | None = None) -> int:
    if df.empty:
        return 0

    valid_df = validate_event_dataframe(df)
    columns = ", ".join(EVENT_COLUMNS)
    query = f"INSERT INTO {TABLE_NAME} ({columns}) VALUES ({placeholders(len(EVENT_COLUMNS))})"
    rows = [
        EventRecord.from_mapping(record).to_row()
        for record in valid_df.to_dict(orient="records")
    ]

    with transaction() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, rows)
        log_action(
            tabla=TABLE_NAME,
            accion="insert_bulk",
            usuario_id=usuario_id,
            detalle=f"{len(rows)} hallazgo(s) insertado(s)",
            conn=conn,
        )

    return len(rows)


def get_all_data() -> pd.DataFrame:
    columns = ", ".join(EVENT_READ_COLUMNS)
    query = f"SELECT {columns} FROM {TABLE_NAME} ORDER BY fecha DESC, id DESC"
    with get_connection() as conn:
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
    return pd.DataFrame(rows, columns=column_names)


def delete_all_data(usuario_id: int | None = None) -> None:
    with transaction() as conn:
        conn.execute(f"DELETE FROM {TABLE_NAME}")
        log_action(
            tabla=TABLE_NAME,
            accion="delete_all",
            usuario_id=usuario_id,
            detalle="Borrado total de hallazgos",
            conn=conn,
        )
