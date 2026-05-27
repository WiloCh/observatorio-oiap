import pandas as pd

from src.database.connection import get_connection
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


def insert_dataframe(df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    valid_df = validate_event_dataframe(df)

    query = f"""
    INSERT INTO {TABLE_NAME} (
        fecha, pais, region, programa, tema, tipo_fuente, fuente,
        titulo, descripcion, nivel_riesgo, nivel_oportunidad,
        relevancia, decision_impacto, accion_recomendada, derivacion,
        estado_seguimiento, observaciones
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    rows = [
        EventRecord.from_mapping(record).to_row()
        for record in valid_df.to_dict(orient="records")
    ]

    with get_connection() as conn:
        conn.executemany(query, rows)
        conn.commit()

    return len(rows)


def get_all_data() -> pd.DataFrame:
    columns = ", ".join(EVENT_READ_COLUMNS)
    query = f"SELECT {columns} FROM {TABLE_NAME} ORDER BY fecha DESC, id DESC"
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def delete_all_data() -> None:
    with get_connection() as conn:
        conn.execute(f"DELETE FROM {TABLE_NAME}")
        conn.commit()
