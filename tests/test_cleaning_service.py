import pandas as pd

from src.domain.constants import EVENT_COLUMNS
from src.services.cleaning_service import (
    clean_dataframe,
    generate_template,
    normalize_date,
    normalize_level,
    normalize_score,
)


def test_generate_template_uses_event_columns():
    assert list(generate_template().columns) == EVENT_COLUMNS


def test_normalize_date_returns_iso_date_or_empty_string():
    assert normalize_date("2026/05/25") == "2026-05-25"
    assert normalize_date("no es fecha") == ""


def test_normalize_score_clamps_to_allowed_range():
    assert normalize_score("-2") == 0
    assert normalize_score("3.8") == 3
    assert normalize_score("9") == 5
    assert normalize_score("") == 0


def test_normalize_level_accepts_known_values():
    assert normalize_level(" alto ") == "Alto"
    assert normalize_level("desconocido") == ""


def test_clean_dataframe_adds_missing_columns_and_drops_invalid_rows():
    raw_df = pd.DataFrame(
        [
            {"fecha": "2026-05-25", "pais": " Ecuador ", "tema": "IA", "titulo": "Evento"},
            {"fecha": "2026-05-25", "pais": "Ecuador", "tema": "IA", "titulo": "Evento"},
            {"fecha": "2026-05-26", "pais": "Perú", "tema": "Datos", "titulo": ""},
        ]
    )

    clean_df = clean_dataframe(raw_df)

    assert list(clean_df.columns) == EVENT_COLUMNS
    assert len(clean_df) == 1
    assert clean_df.loc[0, "pais"] == "Ecuador"
    assert clean_df.loc[0, "estado_seguimiento"] == "Detectado"
