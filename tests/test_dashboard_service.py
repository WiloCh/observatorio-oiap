from datetime import date

import pandas as pd

from src.services.dashboard_service import (
    apply_dashboard_filters,
    get_date_bounds,
    get_filter_options,
    has_custom_filter,
)


def test_get_filter_options_returns_sorted_non_empty_values():
    df = pd.DataFrame({"pais": ["Perú", "", None, "Ecuador"]})

    assert get_filter_options(df, "pais") == ["Ecuador", "Perú"]


def test_apply_dashboard_filters_filters_each_selected_dimension():
    df = pd.DataFrame(
        [
            {
                "pais": "Ecuador",
                "programa": "A",
                "tema": "IA",
                "clasificacion_alerta": "Alta",
                "derivacion": "Think Tank",
                "estado_seguimiento": "Elevado",
            },
            {
                "pais": "Perú",
                "programa": "B",
                "tema": "Datos",
                "clasificacion_alerta": "Monitoreo",
                "derivacion": "Monitoreo continuo",
                "estado_seguimiento": "Detectado",
            },
        ]
    )

    filtered = apply_dashboard_filters(
        df,
        ["Ecuador"],
        ["A"],
        ["IA"],
        ["Alta"],
        ["Think Tank"],
        ["Elevado"],
    )

    assert len(filtered) == 1
    assert filtered.iloc[0]["pais"] == "Ecuador"


def test_apply_dashboard_filters_filters_by_date_range():
    df = pd.DataFrame(
        [
            {"fecha": pd.Timestamp("2026-05-01"), "pais": "Ecuador", "programa": "A", "tema": "IA", "clasificacion_alerta": "Alta"},
            {"fecha": pd.Timestamp("2026-06-01"), "pais": "Ecuador", "programa": "A", "tema": "IA", "clasificacion_alerta": "Alta"},
        ]
    )

    filtered = apply_dashboard_filters(
        df,
        [],
        [],
        [],
        [],
        selected_date_range=(date(2026, 5, 1), date(2026, 5, 31)),
    )

    assert len(filtered) == 1
    assert filtered.iloc[0]["fecha"] == pd.Timestamp("2026-05-01")


def test_get_date_bounds_returns_min_and_max_dates():
    df = pd.DataFrame({"fecha": [pd.Timestamp("2026-05-01"), pd.Timestamp("2026-06-01")]})

    assert get_date_bounds(df) == (date(2026, 5, 1), date(2026, 6, 1))


def test_has_custom_filter_detects_partial_selection():
    assert has_custom_filter(["Ecuador"], ["Ecuador", "Perú"])
    assert not has_custom_filter(["Ecuador", "Perú"], ["Ecuador", "Perú"])
