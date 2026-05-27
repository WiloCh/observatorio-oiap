import pandas as pd
import pytest

from src.database.repository import validate_event_dataframe
from src.domain.constants import EVENT_COLUMNS


def test_validate_event_dataframe_rejects_missing_columns():
    with pytest.raises(ValueError, match="Faltan columnas requeridas"):
        validate_event_dataframe(pd.DataFrame([{"titulo": "Evento"}]))


def test_validate_event_dataframe_rejects_invalid_domain_values():
    row = {column: "" for column in EVENT_COLUMNS}
    row["titulo"] = "Evento"
    row["nivel_riesgo"] = "Gigante"

    with pytest.raises(ValueError, match="Nivel de riesgo inválido"):
        validate_event_dataframe(pd.DataFrame([row]))


def test_validate_event_dataframe_accepts_valid_rows():
    row = {column: "" for column in EVENT_COLUMNS}
    row["titulo"] = "Evento"
    row["nivel_riesgo"] = "Alto"
    row["nivel_oportunidad"] = "Bajo"
    row["relevancia"] = 4
    row["estado_seguimiento"] = "Detectado"

    valid_df = validate_event_dataframe(pd.DataFrame([row]))

    assert list(valid_df.columns) == EVENT_COLUMNS
