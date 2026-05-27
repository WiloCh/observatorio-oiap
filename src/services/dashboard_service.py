import pandas as pd


ALL_FILTER_LABEL = "Todos"
CUSTOM_FILTER_LABEL = "Personalizar"


def get_filter_options(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df.columns:
        return []
    values = [value for value in df[column].dropna().unique() if str(value).strip()]
    return sorted(values)


def apply_dashboard_filters(
    df: pd.DataFrame,
    selected_paises: list[str],
    selected_programas: list[str],
    selected_temas: list[str],
    selected_alertas: list[str],
    selected_derivaciones: list[str] | None = None,
    selected_estados: list[str] | None = None,
    selected_date_range: tuple | None = None,
) -> pd.DataFrame:
    filtered = df.copy()

    filters = {
        "pais": selected_paises,
        "programa": selected_programas,
        "tema": selected_temas,
        "clasificacion_alerta": selected_alertas,
        "derivacion": selected_derivaciones or [],
        "estado_seguimiento": selected_estados or [],
    }

    for column, selected_values in filters.items():
        if selected_values:
            filtered = filtered[filtered[column].isin(selected_values)]

    if selected_date_range and len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
        if start_date and end_date and "fecha" in filtered.columns:
            dates = filtered["fecha"].dt.date
            filtered = filtered[(dates >= start_date) & (dates <= end_date)]

    return filtered


def get_date_bounds(df: pd.DataFrame) -> tuple | None:
    if df.empty or "fecha" not in df.columns:
        return None

    valid_dates = df["fecha"].dropna()
    if valid_dates.empty:
        return None

    return valid_dates.min().date(), valid_dates.max().date()


def has_custom_filter(selected_values: list[str], all_values: list[str]) -> bool:
    return bool(selected_values) and set(selected_values) != set(all_values)
